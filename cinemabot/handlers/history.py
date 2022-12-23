from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from cinemabot.database.connector import get_db
from cinemabot.database.core import get_search_history
from cinemabot.database.models import SearchHistory
from cinemabot.handlers.utils import get_state_safe
from cinemabot.handlers.utils.keyboard_markup import construct_keyboard_markup_for_history
from cinemabot.state import UserState


def construct_replay_text_in_history(search_history: list[SearchHistory]) -> str:
    if not search_history:
        return "Ничего не найдено. Попробуйте поискать что-нибудь командой `/find`"
    res = [f"- ({request.dt_created.date()}) `{request.request_text}`" for request in search_history]
    title = "*История поисковых запросов:*\n\n"
    return title + "\n".join(res)


async def history_command_executor(message: Message, state: FSMContext) -> None:
    await state.set_state(UserState.history_state.state)

    state_data = await get_state_safe(state)
    state_data.update({"history": {"page_number": 1}})
    await state.set_data(state_data)

    db = await get_db()
    async with db.get_replica_session() as session:
        search_history = await get_search_history(
            session=session,
            user_id=message.from_user.id,
            page_number=1,
        )

    await message.answer(
        text=construct_replay_text_in_history(search_history),
        parse_mode="markdown",
        reply_markup=construct_keyboard_markup_for_history(
            page_number=1,
            is_empty=not bool(search_history),
            need_next=len(search_history) == 10,
        ),
    )


async def get_history_page(callback_query: CallbackQuery, state: FSMContext, is_next_page: bool) -> None:
    state_data = await get_state_safe(state)
    page_number = state_data.get("history", {}).get("page_number", 1)

    if is_next_page:
        page_number += 1
    else:
        page_number -= 1

    state_data.update({"history": {"page_number": page_number}})
    await state.set_data(state_data)

    db = await get_db()
    async with db.get_replica_session() as session:
        search_history = await get_search_history(
            session=session,
            user_id=callback_query.message.chat.id,
            page_number=page_number,
        )
    await callback_query.message.edit_text(
        text=construct_replay_text_in_history(search_history),
        parse_mode="markdown",
        reply_markup=construct_keyboard_markup_for_history(
            page_number,
            not search_history,
            len(search_history) == 10,
        ),
    )


async def history_next_page(callback_query: CallbackQuery, state: FSMContext) -> None:
    await get_history_page(
        callback_query=callback_query,
        state=state,
        is_next_page=True,
    )


async def history_prev_page(callback_query: CallbackQuery, state: FSMContext) -> None:
    await get_history_page(
        callback_query=callback_query,
        state=state,
        is_next_page=False,
    )
