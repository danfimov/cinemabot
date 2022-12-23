from asyncio import run
from typing import Any

from aiohttp import ClientSession


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Singleton":  # type: ignore
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)  # noqa
        return cls._instance


class BaseClient(Singleton):
    def __init__(self, base_url: str, header_tokens: dict[str, str], cookies: dict[str, str] | None = None) -> None:
        self.session: ClientSession = ClientSession()
        self.base_url = base_url
        self.header_tokens: dict[str, str] = header_tokens
        self.cookies = cookies

    def make_headers(self, headers: dict[str, Any] | None = None) -> dict[str, Any]:
        if headers is None:
            headers = {}
        headers.update(self.header_tokens)
        return headers

    def __del__(self) -> None:
        run(self.session.close())
