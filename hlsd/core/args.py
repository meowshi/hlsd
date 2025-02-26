import argparse


class Args():
    def __init__(self) -> None:

        args_parser = argparse.ArgumentParser()
        args_parser.add_argument(
            "-j", "--json", help="Json file with config. If not set gets configuration from cli")
        args_parser.add_argument("-t", "--tasks", default=1, type=int,
                                 help="amount of fetching tasks. More = faster = mode RAM")
        args_parser.add_argument(
            "-u", "--uri", help="playlist URL. Required if config file is not used")
        args_parser.add_argument(
            "-n", "--name", type=str, help="name of a file where resul will be stored. without extension")
        args = args_parser.parse_args()

        self.json: str = args.json
        self.tasks: int = args.tasks
        self.uri: str = args.uri
        self.name: str = args.name
