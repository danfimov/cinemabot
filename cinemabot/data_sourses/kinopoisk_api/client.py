from typing import Any
from urllib.parse import urljoin

from cashews import cache
from starlette import status

from cinemabot.config import get_settings
from cinemabot.data_sourses.kinopoisk_api.errors import FilmNotFound
from cinemabot.data_sourses.utils import BaseClient


settings = get_settings()


class KinopoiskClient(BaseClient):  # noqa
    def __init__(self) -> None:
        super(KinopoiskClient, self).__init__(base_url="https://kinopoiskapiunofficial.tech/", header_tokens={"X-API-KEY": settings.KINOPOISK_API_KEY})

    @cache(ttl="24h", key="{keyword}")
    async def search_film_with_keyword(self, keyword: str) -> dict[str, Any]:
        async with self.session.get(
            urljoin(self.base_url, "api/v2.1/films/search-by-keyword"),
            params={"keyword": keyword},
            headers=self.make_headers(),
        ) as response:
            response_data = await response.json()
            if response.status != status.HTTP_200_OK or not response_data["films"]:
                raise FilmNotFound
        return response_data

    @cache(ttl="24h", key="{film_kinopoisk_id}")
    async def get_film_details(self, film_kinopoisk_id: int) -> dict[str, Any]:
        async with self.session.get(
            urljoin(self.base_url, f"api/v2.2/films/{film_kinopoisk_id}"),
            headers=self.make_headers(),
        ) as response:
            response_data = await response.json()
            if response.status != status.HTTP_200_OK:
                raise FilmNotFound
        return response_data

    @cache(ttl="24h", key="{url}")
    async def get_image_size(self, url: str) -> int:
        async with self.session.get(url) as response:
            return int(response.headers["Content-Length"])
