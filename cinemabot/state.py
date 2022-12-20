from aiogram.dispatcher.filters.state import State, StatesGroup


class UserState(StatesGroup):  # type: ignore
    find_state = State()
    history_state = State()
    stats_state = State()


__all__ = [
    "UserState",
]
