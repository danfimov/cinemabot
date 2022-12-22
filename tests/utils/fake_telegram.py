from typing import Any

import aresponses
from aiogram import Bot


class FakeTelegram(aresponses.ResponsesMockServer):  # type: ignore
    def __init__(
        self,
        message_data: list[Any] | dict[Any, Any],
        bot: Bot | None = None,
        **kwargs: dict[Any, Any],
    ) -> None:
        super().__init__(**kwargs)
        self._body, self._headers = self.parse_data(message_data)

        if isinstance(bot, Bot):
            Bot.set_current(bot)

    async def __aenter__(self) -> None:
        await super().__aenter__()
        _response = self.Response(text=self._body, headers=self._headers, status=200, reason='OK')
        self.add(self.ANY, response=_response)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        if hasattr(self, 'monkeypatch'):
            self.monkeypatch.undo()
        await super().__aexit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def parse_data(message_data: list[Any] | dict[Any, Any]) -> tuple[str, dict[str, str]]:
        from aiogram.utils import json
        from aiogram.utils.payload import _normalize

        _body = '{"ok":true,"result":' + json.dumps(_normalize(message_data)) + '}'
        _headers = {'Server': 'nginx/1.12.2',
                    'Date': 'Tue, 03 Apr 2018 16:59:54 GMT',
                    'Content-Type': 'application/json',
                    'Content-Length': str(len(_body)),
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Expose-Headers': 'Content-Length,Content-Type,Date,Server,Connection',
                    'Strict-Transport-Security': 'max-age=31536000; includeSubdomains'}
        return _body, _headers
