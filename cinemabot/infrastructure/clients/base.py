from asyncio import run
from typing import Any

from aiohttp import ClientSession


class BaseAiohttpClient:
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
