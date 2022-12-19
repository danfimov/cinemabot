from typing import Any


def process_base_film_info(film_info: dict[str, Any]) -> dict[str, Any]:
    return {
        "kinopoisk_id": film_info["filmId"],
        "name_ru": film_info["nameRu"],
        "name_eng": film_info.get("nameEn", None),
        "year": int(film_info["year"]),
        "description": film_info["description"],
        "genre": [genre_object["genre"] for genre_object in film_info["genres"]],
        "poster_url": film_info["posterUrl"],
    }


def process_detail_film_info(film_info: dict[str, Any]) -> dict[str, Any]:
    return {
        "kinopoisk_id": film_info["kinopoiskId"],
        "name_ru": film_info["nameRu"],
        "name_eng": film_info.get("nameEn", None),
        "year": int(film_info["year"]),
        "description": film_info["description"],
        "genre": [genre_object["genre"] for genre_object in film_info["genres"]],
        "poster_url": film_info["posterUrl"],
        "people_rating": film_info["ratingKinopoisk"],
        "critics_rating": film_info["ratingFilmCritics"],
        "link": film_info["webUrl"],
        "minutes": film_info["filmLength"] % 60 if film_info["filmLength"] is not None else None,
        "hours": film_info["filmLength"] // 60 if film_info["filmLength"] is not None else None,
    }


def construct_movie_description_in_find(film_details):
    if film_details["hours"] is not None or film_details["minutes"] is not None:
        hours = f"{film_details['hours']} ч" if film_details["hours"] else ""
        minutes = f"{film_details['minutes']} мин" if film_details["minutes"] else ""
        duration = "".join(["_Продолжительность_: ", hours, minutes])
    else:
        duration = ""

    genres = "_Жанр_: " + (", ".join(film_details["genre"]) if film_details["genre"] else "-")
    title = f"*{film_details['name_ru']} [{film_details['year']}]*"

    rating = (
        f"_Рейтинг зрителей/критиков_: {film_details['people_rating'] or 'x'} / {film_details['critics_rating'] or 'x'}"
    )

    return (
        f"{title}\n\n"
        f"{genres}\n"
        f"{duration}\n"
        f"_Год выхода_: {film_details['year']}\n"
        f"{rating}\n\n"
        f"_Описание_:\n{film_details['description']}"
    )
