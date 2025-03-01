# Description
Simple hls streams downloader.
# Usage
## CLI configuration
```
uv run -m hlsd.main -t <number_of_task> -n <stream_name> -u <master_uri>
```
## JSON configuration
Example json in example folder.
```
uv run -m hlsd.main -j <path_to_json>
```
# Not suppoted
- segments decoding
- i-frame playlists
- merging audio and video playlists
- probably more

# Tested
- twitch VODs
- some sites sites that streams shows (example: https://sp.freehat.cc/)