from typing import Any

from starlette import status

from cinemabot.config import get_settings
from cinemabot.data_sourses.kinopoisk_api.errors import FilmNotFound
from cinemabot.data_sourses.utils import BaseClient


settings = get_settings()


class KinopoiskClient(BaseClient):  # noqa
    def __init__(self):
        super(KinopoiskClient, self).__init__(
            base_url="https://kinopoiskapiunofficial.tech/", header_tokens={"X-API-KEY": settings.KINOPOISK_API_KEY}
        )

    async def search_film_with_keyword(self, keyword: str) -> dict[str, Any]:
        async with self.session.get(
            self.base_url + "api/v2.1/films/search-by-keyword",
            params={"keyword": keyword},
            headers=self.make_headers(),
        ) as response:
            if response.status != status.HTTP_200_OK or not (await response.json())["films"]:
                raise FilmNotFound
            print(f"{response.status = }")
            return await response.json()

    async def get_film_details(self, film_kinopoisk_id: int) -> dict[str, Any]:
        async with self.session.get(
            self.base_url + f"api/v2.2/films/{film_kinopoisk_id}",
            headers=self.make_headers(),
        ) as response:
            if response.status != status.HTTP_200_OK:
                raise FilmNotFound
            return await response.json()
