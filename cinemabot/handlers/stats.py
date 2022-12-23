from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from cinemabot.database.connector import get_db
from cinemabot.database.core import get_stats
from cinemabot.handlers.utils import get_state_safe
from cinemabot.handlers.utils.keyboard_markup import construct_keyboard_markup_for_stats
from cinemabot.state import UserState


def construct_replay_text_in_stats(stats: list[tuple[int, str]]) -> str:
    if not stats:
        return "Больше статистики нет. Попробуйте поискать что-нибудь командой `/find`"
    res = [f"- ({stat[0]}) `{stat[1]}`" for stat in stats]

    title = "*Статистика показов фильмов:*\n\n"
    return title + "\n".join(res)


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
    await callback_query.message.edit_text(
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
