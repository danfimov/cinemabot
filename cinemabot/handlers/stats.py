from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from cinemabot.database.connector import get_db
from cinemabot.database.core import get_stats
from cinemabot.handlers.utils import get_state_safe
from cinemabot.state import UserState


def construct_keyboard_markup_for_stats(
    page_number: int,
    is_empty: bool,
    need_next: bool,
) -> InlineKeyboardMarkup | None:
    keyboard_markup = InlineKeyboardMarkup()
    button_prev = InlineKeyboardButton("Назад", callback_data="stats_command_prev_button")
    button_next = InlineKeyboardButton("Вперёд", callback_data="stats_command_next_button")

    if is_empty:
        if page_number > 1:
            keyboard_markup.add(button_prev)
            return keyboard_markup
        else:
            return None

    if page_number > 1:
        if need_next:
            keyboard_markup.add(button_prev, button_next)
        else:
            keyboard_markup.add(button_prev)
    else:
        if need_next:
            keyboard_markup.add(button_next)
        else:
            return None
    return keyboard_markup


def construct_replay_text_in_stats(stats: list[tuple[int, str]]) -> str:
    if not stats:
        return "Больше статистики нет. Попробуйте поискать что-нибудь командой `/find`"
    res = [f"- ({stat[0]}) `{stat[1]}`" for stat in stats]
    return "\n".join(res)


async def stats_command_executor(message: Message, state: FSMContext) -> None:
    await state.set_state(UserState.stats_state.state)

    state_data = await get_state_safe(state)
    state_data.update({"stats": {"page_number": 1}})
    await state.set_data(state_data)

    db = await get_db()
    async with db.get_replica_session() as session:
        statistic = await get_stats(
            session=session,
            user_id=message.from_user.id,
            page_number=1,
        )

    await message.answer(
        text=construct_replay_text_in_stats(statistic),
        parse_mode="markdown",
        reply_markup=construct_keyboard_markup_for_stats(
            page_number=1,
            is_empty=not bool(statistic),
            need_next=len(statistic) == 10,
        ),
    )


async def get_stats_page(callback_query: CallbackQuery, state: FSMContext, is_next_page: bool) -> None:
    state_data = await get_state_safe(state)
    page_number = state_data.get("stats", {}).get("page_number", 1)

    if is_next_page:
        page_number += 1
    else:
        page_number -= 1

    state_data.update({"stats": {"page_number": page_number}})
    await state.set_data(state_data)

    db = await get_db()
    async with db.get_replica_session() as session:
        statistic = await get_stats(
            session=session,
            user_id=callback_query.message.chat.id,
            page_number=page_number,
        )
    await callback_query.message.answer(
        text=construct_replay_text_in_stats(statistic),
        parse_mode="markdown",
        reply_markup=construct_keyboard_markup_for_stats(
            page_number,
            not statistic,
            len(statistic) == 10,
        ),
    )


async def stats_next_page(callback_query: CallbackQuery, state: FSMContext) -> None:
    await get_stats_page(
        callback_query=callback_query,
        state=state,
        is_next_page=True,
    )


async def stats_prev_page(callback_query: CallbackQuery, state: FSMContext) -> None:
    await get_stats_page(
        callback_query=callback_query,
        state=state,
        is_next_page=False,
    )
