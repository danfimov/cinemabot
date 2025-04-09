import aiogram
from aiogram import filters, types
from aiogram.fsm.context import FSMContext

from cinemabot import dependencies
from cinemabot.handlers.utils import get_state_safe
from cinemabot.handlers.utils.keyboard_markup import construct_keyboard_markup_for_history
from cinemabot.infrastructure.database.schemas import SearchHistory
from cinemabot.state import UserState


router = aiogram.Router()


def construct_replay_text_in_history(search_history: list[SearchHistory]) -> str:
    if not search_history:
        return "Ничего не найдено. Попробуйте поискать что-нибудь командой `/find`"
    res = [f"- ({request.created_at.date()}) `{request.request_text}`" for request in search_history]
    title = "*История поисковых запросов:*\n\n"
    return title + "\n".join(res)


@router.message(filters.Command(commands=["history"]))
async def history_command_executor(message: types.Message, state: FSMContext) -> None:
    await state.set_state(UserState.history_state.state)

    state_data = await get_state_safe(state)
    state_data.update({"history": {"page_number": 1}})
    await state.set_data(state_data)

    storage = dependencies.get_storage_repository()
    search_history = await storage.get_search_history(
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


async def _get_history_page(callback_query: types.CallbackQuery, state: FSMContext, is_next_page: bool) -> None:
    state_data = await get_state_safe(state)
    page_number = state_data.get("history", {}).get("page_number", 1)

    if is_next_page:
        page_number += 1
    else:
        page_number -= 1

    state_data.update({"history": {"page_number": page_number}})
    await state.set_data(state_data)

    storage = dependencies.get_storage_repository()
    search_history = await storage.get_search_history(
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


@router.callback_query(
    aiogram.F.data == "history_command_next_button",
    filters.StateFilter(UserState.history_state),
)
async def history_next_page(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await _get_history_page(
        callback_query=callback_query,
        state=state,
        is_next_page=True,
    )


@router.callback_query(
    aiogram.F.data == "history_command_prev_button",
    filters.StateFilter(UserState.history_state),
)
async def history_prev_page(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await _get_history_page(
        callback_query=callback_query,
        state=state,
        is_next_page=False,
    )
