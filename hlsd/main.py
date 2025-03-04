import asyncio
import logging

from hlsd.core.args import Args
from hlsd.core.config import Config
from hlsd.core.downloader import ADownloader
from hlsd.core.fetcher.aiohttp_fetcher import AiohttpFetcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s %(message)s",
    handlers=[
        logging.FileHandler("hlsd.log"),
    ]
)


async def main():
    args = Args()

    if args.json:
        try:
            config = Config.from_json_file(args.json)
        except FileNotFoundError:
            print(f"config file {args.json} do not exists.")
            return
    else:
        config = Config.from_args(args)

    async with AiohttpFetcher() as f:
        await ADownloader(config, f).run()


if __name__ == "__main__":
    asyncio.run(main())
