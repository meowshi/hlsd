import asyncio
import aiohttp
import logging

log = logging.getLogger(__name__)


async def fetch_segment(client: aiohttp.ClientSession, uri: str) -> bytes:
    log.info(f"fetching {uri}")
    async with client.get(uri) as res:
        return await res.read()


async def fetch_segments(client: aiohttp.ClientSession, uris: list[str]):
    results = await asyncio.gather(*[fetch_segment(client, uri) for uri in uris])
    return results
