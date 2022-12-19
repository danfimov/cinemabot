from typing import Any

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from cinemabot.data_sourses.kinopoisk_api.client import KinopoiskClient
from cinemabot.data_sourses.kinopoisk_api.errors import FilmNotFound
from cinemabot.database.connector import get_db
from cinemabot.database.core import add_request_to_history, increase_number_of_film_view
from cinemabot.handlers.utils import get_state_safe
from cinemabot.state import UserState


def construct_keyboard_markup_for_find() -> InlineKeyboardMarkup:
    keyboard_markup = InlineKeyboardMarkup()
    button_continue = InlineKeyboardButton("⏭", callback_data="find_command_next_button")
    button_details = InlineKeyboardButton("▶️", callback_data="find_command_detail_button")
    button_stop = InlineKeyboardButton("⏹", callback_data="find_command_stop_button")

    keyboard_markup.add(button_details, button_continue, button_stop)

    return keyboard_markup


def construct_keyboard_markup_for_detail_view(link: str) -> InlineKeyboardMarkup:
    keyboard_markup = InlineKeyboardMarkup()
    button_with_link = InlineKeyboardButton("Смотреть на Кинопоиске", url=link)
    button_continue = InlineKeyboardButton("Следующий фильм в поиске", callback_data="find_command_next_button")

    keyboard_markup.add(button_with_link)
    keyboard_markup.add(button_continue)

    return keyboard_markup


async def get_search_result(film_name: str) -> dict[str, Any]:
    client = KinopoiskClient()
    return await client.search_film_with_keyword(film_name)


async def get_film_detail(film_kinopoisk_id: int) -> dict[str, Any]:
    client = KinopoiskClient()
    return await client.get_film_details(film_kinopoisk_id)


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


async def find_command_executor(message: Message, state: FSMContext) -> None:
    film_name = message.text.lstrip("/find ")
    print(f"{film_name=}")
    if not film_name:
        await message.answer(
            "Введите название фильма. Например, `/find Груз 200`",
            parse_mode="markdown",
            reply=False,
        )
        return

    db = await get_db()
    async with db.get_master_session() as session:
        await add_request_to_history(
            session=session,
            user_id=message.from_user.id,
            request_text=film_name,
        )

        try:
            film_info_from_client = await get_search_result(film_name)
        except FilmNotFound:
            await message.answer(f"К сожалению нам не удалось найти фильм с названием '{film_name}'")
            return

        await state.set_state(UserState.find_state.state)
        state_data = await get_state_safe(state)
        base_film_info = process_base_film_info(film_info_from_client["films"][0])
        state_data.update({"find_result": film_info_from_client, "find_last_viewed": base_film_info})
        await state.set_data(state_data)

        await increase_number_of_film_view(
            session=session,
            user_id=message.from_user.id,
            film_kinopoisk_id=base_film_info["kinopoisk_id"],
            film_name_ru=base_film_info["name_ru"],  # if film does not exist in database yet
            film_name_eng=base_film_info["name_eng"],
        )

    await message.answer_photo(
        photo=base_film_info["poster_url"],
        caption=f"*{base_film_info['name_ru']} [{base_film_info['year']}]*\n\n"
        f"_Жанр_: {', '.join(base_film_info['genre'])}\n\n"
        f"_Описание_:\n{base_film_info['description']}",
        parse_mode="markdown",
        reply_markup=construct_keyboard_markup_for_find(),
    )


async def next_movie_in_find(callback_query: CallbackQuery, state: FSMContext):
    print(callback_query)
    await callback_query.message.answer("#TODO: implement later")  # TODO: вытаскивать следующий фильм из поиска


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


async def movie_description_in_find(callback_query: CallbackQuery, state: FSMContext):
    state_data = await get_state_safe(state)
    kinopoisk_id = state_data["find_last_viewed"]["kinopoisk_id"]

    try:
        film_details = process_detail_film_info(await get_film_detail(kinopoisk_id))
    except FilmNotFound:
        await callback_query.message.answer(
            "Извините, сервис временно недоступен",
            parse_mode="markdown",
        )
        return

    await callback_query.message.answer_photo(
        photo=film_details["poster_url"],
        caption=construct_movie_description_in_find(film_details),
        parse_mode="markdown",
        reply_markup=construct_keyboard_markup_for_detail_view(film_details["link"]),
    )


async def cancel_find(callback_query: CallbackQuery, state: FSMContext) -> None:
    state_data = await get_state_safe(state)
    state_data["find"] = None
    await state.set_data(state_data)
    await state.reset_state()

    await callback_query.message.answer("Процесс поиска окончен.")


async def action_in_canceled_find(callback_query: CallbackQuery):
    print(callback_query)
    await callback_query.message.answer(
        "Вы закончили этот поиск. Чтобы начать новый, используйте команду `/find`",
        parse_mode="Markdown",
    )
