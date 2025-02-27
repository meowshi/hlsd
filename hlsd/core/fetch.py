import asyncio
import m3u8
import aiohttp
import logging
from os import abort

log = logging.getLogger(__name__)


async def fetch_segment(client: aiohttp.ClientSession, segment: m3u8.Segment) -> bytes:
    if not segment.uri:
        raise Exception("empty segment uri")

    uri = segment.base_uri + "/" + \
        segment.uri if not segment.uri.startswith("http") else segment.uri

    log.info(f"fetching {uri}")
    async with client.get(uri) as res:
        body = await res.read()
        if segment.media_sequence is None:
            log.error(f"segment media sequence is None: {segment.uri}")
            abort()
        return body


async def fetch_segments(client: aiohttp.ClientSession, segments: list[m3u8.Segment]):
    results = await asyncio.gather(*[fetch_segment(client, segment) for segment in segments])
    return results
