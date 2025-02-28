import logging
from typing import Self
import aiohttp
import ffmpeg

from hlsd.core.config import Config
from hlsd.core import fetch, format
from hlsd.core.playlist import Playlist

log = logging.getLogger(__name__)


# Async downloader
class ADownloader():
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        self._client = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.close()

    async def run(self):
        if not self._client:
            return

        print(f"Playlists to download: {len(self._config.playlists)}")

        playlists = [Playlist(playlist_config)
                     for playlist_config in self._config.playlists]
        for playlist in playlists:
            await playlist.setup(self._client)

        for playlist in playlists:
            ffmpeg_process = ffmpeg.input("pipe:0", f="mpegts").output(
                filename=f"{playlist.name}.mp4", c="copy", f="mp4").run_async(pipe_stdin=True, pipe_stderr=True, overwrite_output=True)
            if not ffmpeg_process.stdin:
                print(f"skipping {playlist.name}")
                log.info("ffmpeg process stdin is None. Skipping")
                continue

            # TODO: проверить что эту проверку можно убрать
            if not playlist.m3u8_playlist:
                continue

            segments_count = len(playlist.m3u8_playlist.segments)
            print(
                f"Playlist {playlist.name} has {segments_count} segments.")

            downloaded_segments = 0
            downloaded_bytes = 0

            step = self._config.tasks
            rng = (0, step)

            while rng[0] < segments_count:

                print(
                    f'\r[~{format.size(downloaded_bytes)} | {round(downloaded_segments/segments_count*100, 1)}%] Downloading {rng}', end="", flush=True)

                results = await fetch.fetch_segments(self._client, playlist[rng[0]:rng[1]])
                for result in results:
                    ffmpeg_process.stdin.write(result)
                    downloaded_bytes += len(result)

                downloaded_segments += rng[1] - rng[0]
                rng = (rng[1], min(rng[1]+step, segments_count))

            print(
                f'\r[~{format.size(downloaded_bytes)} | {round(downloaded_segments/segments_count*100, 1)}%] Downloaded', end="", flush=True)
            print()

            ffmpeg_process.stdin.close()
            ffmpeg_process.wait()
