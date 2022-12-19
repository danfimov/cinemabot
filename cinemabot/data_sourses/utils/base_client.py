from typing import Any

from aiohttp import ClientSession


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)  # noqa
        return cls._instance


class BaseClient(Singleton):
    def __init__(self, base_url: str, header_tokens: dict[str, str]) -> None:
        self.session: ClientSession = ClientSession()
        self.base_url = base_url
        self.header_tokens: dict[str, str] = header_tokens

    def make_headers(self, headers: dict[str, Any] | None = None) -> dict[str, Any]:
        if headers is None:
            headers = {}
        headers.update(self.header_tokens)
        return headers

    def __del__(self):
        self.session.close()
