from typing import Any

from aiogram.dispatcher import FSMContext


async def get_state_safe(state: FSMContext) -> dict[str, Any]:
    state_data = await state.get_data(default=None)
    if state_data is None:
        return {}
    return state_data
