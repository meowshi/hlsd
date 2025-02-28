from abc import ABC, abstractmethod


class AFetcher(ABC):
    @abstractmethod
    async def fetch_bytes(self, uri: str) -> bytes: ...

    @abstractmethod
    async def fetch_str(self, uri: str) -> str: ...

    @abstractmethod
    async def gather_bytes(self, uris: list[str]) -> list[bytes]: ...
