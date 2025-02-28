import json
from typing import Self

from pydantic import BaseModel

from hlsd.core.config.playlist_config import PlaylistConfig
from hlsd.core.args import Args


class Config(BaseModel):

    tasks: int = 1
    playlists: list[PlaylistConfig] = []

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        return cls(**json.loads(json_str))

    @classmethod
    def from_json_file(cls, json_file: str) -> Self:
        with open(json_file) as f:
            return cls(**json.load(f))

    @classmethod
    def from_args(cls, args: Args) -> Self:
        return cls(
            tasks=args.tasks,
            playlists=[PlaylistConfig(
                uri=args.uri,
                name=args.name,
            )]
        )
