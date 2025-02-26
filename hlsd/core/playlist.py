import logging
from typing import Any
import uuid
import aiohttp
import m3u8
from pydantic import BaseModel, ConfigDict, Field, field_validator


log = logging.getLogger(__name__)


def uuid4_str() -> str:
    return uuid.uuid4().hex


class Playlist(BaseModel):
    uri: str
    name: str = Field(default_factory=uuid4_str)
    m3u8_playlist: m3u8.M3U8 | None = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True  # чтобы на M3U8 не ругался
    )

    # так мы вроде гарантируем, что если кто-то по ошибке в конфиге решит указать m3u8 это не учтется
    @field_validator("m3u8_playlist")
    def skip_m3u8_playlist(cls, v: Any):
        return None

    async def setup(self, client: aiohttp.ClientSession):
        if self.m3u8_playlist:
            return

        async with client.get(self.uri) as res:
            master = m3u8.loads(await res.text())

        if not master.is_variant:
            # Eсли base_path пустой и segment.uri это просто название файла а не полный uri,
            # то мы предполагаем что base_path будет такой же как и у uri на master
            if not master.base_path and master.segments[0].uri and not master.segments[0].uri.startswith("http"):
                log.info("master base uri is empty and segments uri is incomplete")
                master.base_path = self.uri[:self.uri.rfind('/')]
        else:
            while master.is_variant:
                # надо будет еще учитывать iframe playlists
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
                        self.uri = selected_playlist.uri

        self.m3u8_playlist = master
