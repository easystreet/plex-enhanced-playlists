import os
import sys
import argparse
import shutil
import requests
from plexapi.server import PlexServer
from plexapi.exceptions import NotFound

# Read the Plex server URL and authentication token from environment variables
PLEX_URL = os.environ['PLEX_URL']
PLEX_TOKEN = os.environ['PLEX_TOKEN']

# Connect to the Plex server
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

def add_library(library_name, library_type, folder_path):
    # Check if the library already exists
    try:
        existing_library = plex.library.section(library_name)
        print(f"Library '{library_name}' already exists")
        sys.exit(1)
    except NotFound:
        pass

    # Add the new library
    plex.library.add(name=library_name, type=library_type, agent=None, scanner=None, location=folder_path)
    print(f"Library '{library_name}' added successfully")

def list_playlists():
    print("\nPlaylists:")
    for playlist in plex.playlists():
        print(f"{playlist.title} (items: {len(playlist.items())})")

import shutil

def add_to_playlist(file_paths, playlist_name, library_name):
    # Find or create the playlist
    playlist = None
    for pl in plex.playlists():
        if pl.title == playlist_name:
            playlist = pl
            break
    if playlist is None:
        playlist = plex.createPlaylist(playlist_name, items=[])

    # Get the specified library
    try:
        library = plex.library.section(library_name)
    except NotFound:
        print(f"Library '{library_name}' not found")
        sys.exit(1)

    library_base_path = library.locations[0]

    # Find the media items corresponding to the given file paths and add them to the playlist
    for file_path in file_paths:
        media_item = None
        try:
            media_item = find_media_item_by_file_path(library, file_path)
        except NotFound:
            pass

        if media_item is None:
            # Copy the file to the library folder if it doesn't exist
            print(f"Adding file to library: {file_path}")
            relative_path = os.path.dirname(file_path).split(os.sep)[-1]
            library_subfolder = os.path.join(library_base_path, relative_path)

            if not os.path.exists(library_subfolder):
                os.makedirs(library_subfolder)

            destination_path = os.path.join(library_subfolder, os.path.basename(file_path))
            shutil.copy2(file_path, destination_path)

            # Update the library
            library.update()
            scan_library_folder(library)

            plex.library.refresh()
            media_item = find_media_item_by_file_path(library, destination_path)

        if media_item:
            playlist.addItems(media_item)
        else:
            print(f"Failed to add file to library: {file_path}")
            
def scan_library_folder(library):
    scanner_url = f"{PLEX_URL}/library/sections/{library.key}/refresh"
    headers = {"X-Plex-Token": PLEX_TOKEN}
    response = requests.get(scanner_url, headers=headers)

    if response.status_code == 200:
        print("Library scan started")
    else:
        print(f"Failed to start library scan, status code: {response.status_code}")


def find_media_item_by_file_path(library, file_path):
    for item in library.all():
        for media in item.media:
            if media.parts[0].file == file_path:
                return item
    return None

def create_or_sync_playlist(folder_path, library_name):
    # Get the specified library
    try:
        library = plex.library.section(library_name)
    except NotFound:
        print(f"Library '{library_name}' not found")
        sys.exit(1)

    # Get the folder name and use it as the playlist name
    folder_name = os.path.basename(folder_path)
    playlist_name = folder_name

    # Get the media items in the folder
    media_items = []
    for item in library.all():
        if item.file.startswith(folder_path):
            media_items.append(item)

    if not media_items:
        print(f"No media items found in folder: {folder_path}")
        sys.exit(1)

    # Find or create the playlist
    playlist = None
    for pl in plex.playlists():
        if pl.title == playlist_name:
            playlist = pl
            break

    if playlist is None:
        # Create a new playlist with the media items
        playlist = plex.createPlaylist(playlist_name, items=media_items)
    else:
        # Sync the existing playlist with the media items
        playlist_items = playlist.items()
        for item in media_items:
            if item not in playlist_items:
                playlist.addItems(item)
        for item in playlist_items:
            if item not in media_items:
                playlist.removeItem(item)

def main():
    parser = argparse.ArgumentParser(description="Plex playlist manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subparser for the 'add-library' command
    add_library_parser = subparsers.add_parser("add-library", help="Add a new library")
    add_library_parser.add_argument("library_name", help="Name of the new library")
    add_library_parser.add_argument("library_type", help="Type of the new library (e.g., 'movie', 'show')")
    add_library_parser.add_argument("folder_path", help="Path of the folder containing the library content")

    list_parser = subparsers.add_parser("list", help="List all playlists")

    add_parser = subparsers.add_parser("add", help="Add files to a library and playlist")
    add_parser.add_argument("file_paths", nargs="+", help="List of file paths to add to the playlist")
    add_parser.add_argument("playlist_name", help="Name of the playlist")
    add_parser.add_argument("library_name", help="Name of the library where files will be added")

    create_sync_parser = subparsers.add_parser("create-sync", help="Create or sync a playlist with the media contents of a folder")
    create_sync_parser.add_argument("folder_path", help="Path of the folder containing the media items")
    create_sync_parser.add_argument("library_name", help="Name of the library where the media items are located")

    args = parser.parse_args()

    if args.command == "list":
        list_playlists()
    elif args.command == "add":
        add_to_playlist(args.file_paths, args.playlist_name, args.library_name)
    elif args.command == "create-sync":
        create_or_sync_playlist(args.folder_path, args.library_name)
    elif args.command == "add-library":
        add_library(args.library_name, args.library_type, args.folder_path)

if __name__ == "__main__":
    main()

