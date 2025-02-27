import logging
from typing import Any
import uuid
import aiohttp
import m3u8
from pydantic import BaseModel, ConfigDict, field_validator


log = logging.getLogger(__name__)


def uuid4_str() -> str:
    return uuid.uuid4().hex


class Playlist(BaseModel):
    uri: str
    name: str
    m3u8_playlist: m3u8.M3U8 | None = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True  # чтобы на M3U8 не ругался
    )

    @field_validator("name", mode="before")
    def set_name(cls, v: str | None) -> str:
        return v if v else uuid.uuid4().hex

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
