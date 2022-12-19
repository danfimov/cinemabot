from unittest.mock import MagicMock

from pytest import fixture

from cinemabot.data_sourses.kinopoisk_api.client import KinopoiskClient


SEARCH_FILM_RESULT = {
    "keyword": "Нечто",
    "pagesCount": 7,
    "searchFilmsCountResult": 134,
    "films": [
        {
            "filmId": 8366,
            "nameRu": "Нечто",
            "nameEn": "The Thing",
            "type": "FILM",
            "year": "1982",
            "description": "Команде ученых американской исследовательской...",
            "filmLength": "01:49",
            "countries": [{
                "country": "США"
            }],
            "genres": [{
                "genre": "ужасы"
            }, {
                "genre": "фантастика"
            }],
            "rating": "7.9",
            "ratingVoteCount": 113989,
            "posterUrl": "https://kinopoiskapiunofficial.tech/images/posters/kp/8366.jpg",
            "posterUrlPreview": "https://kinopoiskapiunofficial.tech/images/posters/kp_small/8366.jpg"
        },
    ]
}


@fixture(autouse=True)
async def mock_kinopoisk_api() -> None:
    client = KinopoiskClient()
    client.search_film_with_keyword = MagicMock(return_value=SEARCH_FILM_RESULT)
