import logging
from typing import Self
import aiohttp
import ffmpeg

from hlsd.core import fetch, format
from hlsd.core.config import Config
from hlsd.core.playlist import Playlist

log = logging.getLogger(__name__)


# Async downloader
class ADownloader():
    def __init__(self, config: Config | None = None) -> None:
        if not config:
            config = Config(from_args=True)

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

        print(f"Playlists to download: {len(self._config.uris)}")

        playlists: list[Playlist] = []
        for uri in self._config.uris:
            playlist = Playlist(uri)
            if await playlist.setup(self._client):
                playlists.append(playlist)

        print(f"{len(playlists)}/{len(self._config.uris)} playlists was set up.")

        for playlist in playlists:
            ffmpeg_process = ffmpeg.input("pipe:0").output(
                filename=f"{playlist.name}_ffmpeg.mp4", c="copy", f="mp4").run_async(pipe_stdin=True, pipe_stderr=True, overwrite_output=True)
            if not ffmpeg_process.stdin:
                log.info("ffmpeg process stdin is None")
                continue

            # TODO: проверить что эту проверку можно убрать
            if not playlist.m3u8:
                continue

            segments_count = len(playlist.m3u8.segments)

            print(
                f"Playlist {playlist.name} has {segments_count} segments.")

            downloaded_segments = 0
            downloaded_bytes = 0
            step = self._config.tasks
            rng = (0, step)

            while rng[0] < segments_count:

                print(
                    f'\r[~{format.size(downloaded_bytes)} | {round(downloaded_segments/segments_count*100, 1)}%] Downloading {rng}', end="", flush=True)

                results = await fetch.fetch_segments(self._client, playlist.m3u8.segments[rng[0]:rng[1]])
                # может не очень эффективно
                data = bytes().join(results)
                ffmpeg_process.stdin.write(data)

                downloaded_segments += rng[1] - rng[0]
                downloaded_bytes += len(data)
                rng = (rng[1], min(rng[1]+step, segments_count))

            print(
                f'\r[~{format.size(downloaded_bytes)} | {round(downloaded_segments/segments_count*100, 1)}%] Downloaded', end="", flush=True)
            print()

            ffmpeg_process.stdin.close()
            ffmpeg_process.wait()
