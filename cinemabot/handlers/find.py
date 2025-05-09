from typing import Any

import aiogram
from aiogram import filters, types
from aiogram.fsm.context import FSMContext

from cinemabot import dependencies
from cinemabot.handlers.utils.keyboard_markup import (
    construct_keyboard_markup_for_detail_view,
    construct_keyboard_markup_for_find,
)
from cinemabot.handlers.utils.process_film_info import (
    construct_movie_description_in_find,
    process_base_film_info,
    process_detail_film_info,
)
from cinemabot.handlers.utils.state import get_state_safe
from cinemabot.infrastructure.clients import kinopoisk
from cinemabot.state import UserState


router = aiogram.Router()


async def get_search_result(film_name: str) -> dict[str, Any]:
    client = dependencies.get_kinopoisk_client()
    return await client.search_film_with_keyword(film_name)


async def get_film_detail(film_kinopoisk_id: int) -> dict[str, Any]:
    client = dependencies.get_kinopoisk_client()
    return await client.get_film_details(film_kinopoisk_id)


async def get_poster_size(film_info: dict[str, Any]) -> dict[str, Any]:
    client = dependencies.get_kinopoisk_client()
    film_info.update({"poster_size": await client.get_image_size(film_info["posterUrl"])})
    return film_info


@router.message(filters.Command("find"))
async def find_command_executor(message: types.Message, state: FSMContext) -> None:
    film_name = message.text.lstrip("/find ")
    if not film_name:
        await message.answer(
            "Введите название фильма. Например, `/find Груз 200`",
            parse_mode="markdown",
            reply=False,
        )
        return

    storage = dependencies.get_storage_repository()
    await storage.add_request_to_history(
        user_id=message.from_user.id,
        request_text=film_name,
    )

    try:
        film_info_from_client = await get_search_result(film_name)
    except kinopoisk.FilmNotFoundError:
        await message.answer(f"К сожалению нам не удалось найти фильм с названием '{film_name}'")
        return

    await state.set_state(UserState.find_state.state)
    state_data = await get_state_safe(state)
    film_info = film_info_from_client["films"][0]
    film_info = await get_poster_size(film_info)
    base_film_info = process_base_film_info(film_info)
    state_data.update({"find_result": film_info_from_client, "find_last_viewed": base_film_info})
    await state.set_data(state_data)

    await storage.increase_number_of_film_view(
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


@router.callback_query(
    aiogram.F.data == "find_command_next_button",
    filters.StateFilter(UserState.find_state),
)
async def next_movie_in_find(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    state_data = await get_state_safe(state)
    kinopoisk_id = state_data["find_last_viewed"]["kinopoisk_id"]

    prev_res = state_data["find_result"]

    next_film: dict[str, Any] | None = None
    for index, film in enumerate(prev_res["films"]):
        if film["filmId"] == kinopoisk_id:
            if index != len(prev_res["films"]) - 1:
                next_film = prev_res["films"][index + 1]
            break

    if next_film is None:
        await callback_query.message.answer(
            text="К сожалению не удалось найти больше фильмов с таким названием. "
            "Можете начать новый поиск по команде `/find`",
            parse_mode="markdown",
        )

    next_film = await get_poster_size(next_film)
    base_film_info: dict[str, Any] = process_base_film_info(next_film)  # type: ignore
    state_data.update({"find_last_viewed": base_film_info})
    await state.set_data(state_data)

    storage = dependencies.get_storage_repository()
    await storage.increase_number_of_film_view(
        user_id=callback_query.message.chat.id,
        film_kinopoisk_id=base_film_info["kinopoisk_id"],
        film_name_ru=base_film_info["name_ru"],  # if film does not exist in database yet
        film_name_eng=base_film_info["name_eng"],
    )

    await callback_query.message.answer_photo(
        photo=base_film_info["poster_url"],
        caption=f"*{base_film_info['name_ru']} [{base_film_info['year']}]*\n\n"
        f"_Жанр_: {', '.join(base_film_info['genre'])}\n\n"
        f"_Описание_:\n{base_film_info['description']}",
        parse_mode="markdown",
        reply_markup=construct_keyboard_markup_for_find(),
    )


@router.callback_query(
    aiogram.F.data == "find_command_detail_button",
    filters.StateFilter(UserState.find_state),
)
async def movie_description_in_find(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    state_data = await get_state_safe(state)
    kinopoisk_id = state_data["find_last_viewed"]["kinopoisk_id"]

    try:
        film_details_from_api = await get_film_detail(kinopoisk_id)
        film_details_from_api["poster_size"] = state_data["find_last_viewed"]["poster_size"]
        film_details = process_detail_film_info(film_details_from_api)
    except kinopoisk.FilmNotFoundError:
        await callback_query.message.answer(
            "Извините, сервис временно недоступен",
            parse_mode="markdown",
        )
        return

    await callback_query.message.edit_caption(
        caption=construct_movie_description_in_find(film_details),
        parse_mode="markdown",
        reply_markup=construct_keyboard_markup_for_detail_view(film_details["link"]),
    )


@router.callback_query(
    aiogram.F.data == "find_command_stop_button",
    filters.StateFilter(UserState.find_state),
)
async def cancel_find(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    state_data = await get_state_safe(state)
    state_data["find"] = None
    await state.set_data(state_data)
    await state.set_state(None)

    await callback_query.message.answer("Процесс поиска окончен.")


@router.callback_query(
    (aiogram.F.data == "find_command_stop_button")
    | (aiogram.F.data == "find_command_stop_button")
    | (aiogram.F.data == "find_command_next_button"),
)
async def action_in_canceled_find(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.answer(
        "Вы закончили этот поиск. Чтобы начать новый, используйте команду `/find`",
        parse_mode="Markdown",
    )
