import logging
from typing import overload
import aiohttp
import m3u8

from hlsd.core.config.playlist_config import PlaylistConfig


log = logging.getLogger(__name__)


class Playlist:
    def __init__(self, playlist_config: PlaylistConfig):
        self.uri = playlist_config.uri
        self.name = playlist_config.name
        self.m3u8_playlist: m3u8.M3U8 | None = None

    @overload
    def __getitem__(self, key: int) -> str: ...

    @overload
    def __getitem__(self, key: slice) -> list[str]: ...

    def __getitem__(self, key: int | slice) -> str | list[str]:
        if not self.m3u8_playlist:
            raise Exception("m3u8 is not setup")

        if isinstance(key, int):
            segment = self.m3u8_playlist.segments[key]
            if segment.uri:
                if segment.uri.startswith("http"):
                    return segment.uri
                elif self.m3u8_playlist.base_uri:
                    return self.m3u8_playlist.base_uri + "/" + segment.uri
                else:
                    raise Exception("playlist uri empty")
            else:
                raise Exception("segment uri empty")
        else:
            uris: list[str] = []
            for segment in self.m3u8_playlist.segments[key]:
                if segment.uri:
                    if segment.uri.startswith("http"):
                        uris.append(segment.uri)
                    elif self.m3u8_playlist.base_uri:
                        uris.append(self.m3u8_playlist.base_uri +
                                    "/" + segment.uri)
            return uris

    def __len__(self):
        if not self.m3u8_playlist:
            return 0

        return len(self.m3u8_playlist.segments)

    async def setup(self, client: aiohttp.ClientSession):
        if self.m3u8_playlist:
            return

        async with client.get(self.uri) as res:
            master = m3u8.loads(await res.text())

        if not master.is_variant:
            if len(master.segments) <= 0:
                raise Exception("invalid playlist")

            # Eсли base_uri пустой и segment.uri это просто название файла а не полный uri,
            # то мы предполагаем что base_uri будет такой же как и у uri на master
            if not master.base_uri and master.segments[0].uri and not master.segments[0].uri.startswith("http"):
                log.info("master base uri is empty and segments uri is incomplete")
                # base_path оказалось использовать ненадежно потому что если uri сегмента smth/1.ts
                # "smth" будет обрезано и мы получим невалидную ссылку.
                # поэтому при получении uri сегмента мы будем складывать его uri и base uri
                master.base_uri = self.uri[:self.uri.rfind('/')]
        else:
            while master.is_variant:
                # надо будет еще учитывать iframe playlists
                print("Available playlists:")

                playlists = master.playlists
                for i in range(len(playlists)):
                    media_type = "UNDEFINED"
                    for media in playlists[i].media:
                        if media.type:
                            media_type = media.type
                            break
                    print(
                        f'{i+1}. [{media_type}] {playlists[i].stream_info.resolution}')

                c = int(input("Select: "))
                if not 0 < c <= len(playlists):
                    continue

                selected_playlist = playlists[c-1]
                print(f'You selected: {selected_playlist.uri}')

                if selected_playlist.uri:
                    async with client.get(selected_playlist.uri) as res:
                        master = m3u8.loads(await res.text())
                        master.base_uri = selected_playlist.base_path
                        self.uri = selected_playlist.uri

        self.m3u8_playlist = master
