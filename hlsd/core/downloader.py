import logging
import ffmpeg

from hlsd.core.config import Config
from hlsd.core import format
from hlsd.core.playlist import Playlist
from hlsd.core.fetcher.afetcher import AFetcher

log = logging.getLogger(__name__)


# Async downloader
class ADownloader():
    def __init__(self, config: Config, fetcher: AFetcher) -> None:
        self._config = config
        self._fetcher = fetcher

    async def run(self):
        print(f"Playlists to download: {len(self._config.playlists)}")

        playlists = [Playlist(playlist_config)
                     for playlist_config in self._config.playlists]
        for playlist in playlists:
            await playlist.setup(self._fetcher)

        for playlist in playlists:
            ffmpeg_process = ffmpeg.input("pipe:0", f="mpegts").output(
                filename=f"{playlist.name}.mp4", c="copy", f="mp4").run_async(pipe_stdin=True, pipe_stderr=True, overwrite_output=True)
            if not ffmpeg_process.stdin:
                print(f"skipping {playlist.name}")
                log.info("ffmpeg process stdin is None. Skipping")
                continue

            downloaded_segments = 0
            downloaded_bytes = 0

            step = self._config.tasks
            rng = (0, step)

            segments_count = len(playlist)
            print(
                f"Playlist {playlist.name} has {segments_count} segments.")
            while rng[0] < segments_count:

                print(
                    f'\r[~{format.size(downloaded_bytes)} | {round(downloaded_segments/segments_count*100, 1)}%] Downloading {rng}', end="", flush=True)

                results = await self._fetcher.gather_bytes(playlist[rng[0]:rng[1]])
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
