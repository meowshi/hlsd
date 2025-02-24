import asyncio
import logging

from hlsd.core.downloader import ADownloader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s %(message)s",
    handlers=[
        logging.FileHandler("hlsd.log"),
    ]
)


async def main():
    async with ADownloader() as d:
        await d.run()


if __name__ == "__main__":
    asyncio.run(main())
