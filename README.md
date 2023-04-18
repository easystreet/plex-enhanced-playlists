# Plex Enhanced Playlists

Plex Enhanced Playlists is a Python script that provides additional playlist management features for your Plex server. This script allows you to:

- List all playlists
- Add files to a library and playlist
- Create or sync a playlist with the media contents of a folder

## Prerequisites

- Python 3.6 or later
- PlexAPI python library

## Installation

1. Clone the repository:

git clone https://github.com/yourusername/plex-enhanced-playlists.git

2. Install the required packages:

pip install -r requirements.txt

javascript
Copy code

3. Set up environment variables:

export PLEX_URL=http://your-plex-server-url:32400
export PLEX_TOKEN=your-plex-authentication-token

Replace `your-plex-server-url` with your Plex server URL and `your-plex-authentication-token` with your Plex authentication token.

## Usage

usage: main.py [-h] {list,add,create-sync} ...

Plex playlist manager

positional arguments:
{list,add,create-sync}
list List all playlists
add Add files to a library and playlist
create-sync Create or sync a playlist with the media contents of a folder

optional arguments:
-h, --help show this help message and exit

### Examples

1. List all playlists:

python main.py list

2. Add files to a library and playlist:

python main.py add les.mp4 Les Movies

3. Create or sync a playlist with the media contents of a folder:

python main.py create-sync /path/to/folder Movies

## Adding Windows Explorer Context Menu

To add a context menu option in Windows Explorer for single files:

1. Run the `add_context_menu.reg` file to add the necessary registry keys.

2. Edit the registry keys to match the path of the `main.py` file on your system.

3. Restart the Windows Explorer process by opening the Task Manager, right-clicking on the "Windows Explorer" process, and selecting "Restart".

You should now see a "Add to Plex Playlist" option when you right-click on a single file in Windows Explorer.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.