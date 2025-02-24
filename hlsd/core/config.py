import argparse

from hlsd.core import todo


class Config():
    def __init__(self, from_args: bool = False) -> None:
        if from_args:
            args_parser = argparse.ArgumentParser()
            args_parser.add_argument(
                "-j", "--json", help="Json file with config. If not set gets configuration from cli")
            args_parser.add_argument("-t", "--tasks", default=1, type=int,
                                     help="amount of fetching tasks. More = faster = mode RAM")
            args_parser.add_argument(
                "-u", "--uri", nargs='*', help="playlist URL. Required if config file is not used")
            args = args_parser.parse_args()

            if args.json:
                todo("config from json not implemented", args_parser.print_help)

            if not args.json and not args.uri:
                print("Nowhere to get uri. --json=None, uri=None.")
                args_parser.print_help()
                exit(1)

            self.tasks: int = args.tasks
            self.uris: list[str] = list(args.uri)

        return
