import asyncio
import logging
from typing import Self

import aiohttp
from hlsd.fetcher.afetcher import AFetcher

log = logging.getLogger(__name__)


class AiohttpFetcher(AFetcher):
    def __init__(self):
        self._client = aiohttp.ClientSession()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.close()

    async def fetch_bytes(self, uri: str) -> bytes:
        log.info(f"fetching {uri}")
        async with self._client.get(uri) as res:
            return await res.read()

    async def fetch_str(self, uri: str) -> str:
        async with self._client.get(uri) as res:
            return await res.text()

    async def gather_bytes(self, uris: list[str]) -> list[bytes]:
        return await asyncio.gather(*[self.fetch_bytes(uri) for uri in uris])
