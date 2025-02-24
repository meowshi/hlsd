import logging
import uuid
import aiohttp
import m3u8


log = logging.getLogger(__name__)


class Playlist():
    def __init__(self, uri: str, name: str | None = None, m3u8: m3u8.M3U8 | None = None) -> None:
        self._uri = uri
        self.m3u8 = m3u8

        if name is None:
            self.name = uuid.uuid4().hex

    async def setup(self, client: aiohttp.ClientSession) -> bool:
        async with client.get(self._uri) as res:
            master = m3u8.loads(await res.text())

        if not master.is_variant:
            # Eсли base_path пустой и segment.uri это просто название файла а не полный uri,
            # то мы предполагаем что base_path будет такой же как и у uri на master
            if not master.base_path and master.segments[0].uri and not master.segments[0].uri.startswith("http"):
                log.info("master base uri is empty and segments uri is incomplete")
                master.base_path = self._uri[:self._uri.rfind('/')]
        else:
            while master.is_variant:
                # надо будет еще еучитывать iframe playlists
                print("Available playlists:")

                playlists = master.playlists
                for i in range(len(playlists)):
                    print(f'{i+1}. {playlists[i].media[0].name}')

                c = int(input("Select: "))
                if not 0 < c <= len(playlists):
                    continue

                selected_playlist = playlists[c-1]
                print(f'You selected: {selected_playlist.uri}')

                if selected_playlist.uri:
                    async with client.get(selected_playlist.uri) as res:
                        master = m3u8.loads(await res.text())
                        master.base_path = selected_playlist.base_path
                        self._uri = selected_playlist.uri

        self.m3u8 = master
        self.name = input(f"Give {self._uri} a name: ")

        return True
