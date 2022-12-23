from typing import Any


def pick_poster_url(film_info: dict[str, Any]) -> str:
    if film_info["poster_size"] >= 200_000:
        return film_info["posterUrlPreview"]
    return film_info["posterUrl"]


def pick_name_ru(film_info: dict[str, Any]) -> str | None:
    if film_info.get("nameRu", None) is None:
        return film_info.get("nameEn")
    return film_info.get("nameRu", None)


def pick_year(film_info: dict[str, Any]) -> int | str:
    year = film_info.get("year", "год выхода неизвестен")
    if year == "null":
        return "год выхода неизвестен"
    return year


def process_base_film_info(film_info: dict[str, Any]) -> dict[str, Any]:
    return {
        "kinopoisk_id": film_info["filmId"],
        "name_ru": pick_name_ru(film_info),
        "name_eng": film_info.get("nameEn", None),
        "year": pick_year(film_info),
        "description": film_info.get("description", "(описание отсутствует)"),
        "genre": [genre_object["genre"] for genre_object in film_info["genres"]],
        "poster_url": pick_poster_url(film_info),
        "poster_size": film_info["poster_size"],
    }


def process_detail_film_info(film_info: dict[str, Any]) -> dict[str, Any]:
    return {
        "kinopoisk_id": film_info["kinopoiskId"],
        "name_ru": pick_name_ru(film_info),
        "name_eng": film_info.get("nameEn", None),
        "year": pick_year(film_info),
        "description": film_info.get("description", "(описание отсутствует)"),
        "genre": [genre_object["genre"] for genre_object in film_info["genres"]],
        "poster_url": pick_poster_url(film_info),
        "people_rating": film_info["ratingKinopoisk"],
        "critics_rating": film_info["ratingFilmCritics"],
        "link": film_info["webUrl"],
        "minutes": film_info["filmLength"] % 60 if film_info["filmLength"] is not None else None,
        "hours": film_info["filmLength"] // 60 if film_info["filmLength"] is not None else None,
    }


def construct_movie_description_in_find(film_details: dict[str, Any]) -> str:
    if film_details["hours"] is not None or film_details["minutes"] is not None:
        hours = f"{film_details['hours']} ч " if film_details["hours"] else ""
        minutes = f"{film_details['minutes']} мин" if film_details["minutes"] else ""
        duration = "".join(["_Продолжительность_: ", hours, minutes])
    else:
        duration = ""

    genres = "_Жанр_: " + (", ".join(film_details["genre"]) if film_details["genre"] else "-")
    title = f"*{film_details['name_ru']} [{film_details['year']}]*"

    rating = f"_Рейтинг зрителей/критиков_: {film_details['people_rating'] or 'x'} / {film_details['critics_rating'] or 'x'}"

    return f"{title}\n\n" f"{genres}\n" f"{duration}\n" f"_Год выхода_: {film_details['year']}\n" f"{rating}\n\n" f"_Описание_:\n{film_details['description']}"
