from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def construct_keyboard_markup_for_history(
    page_number: int,
    is_empty: bool,
    need_next: bool,
) -> InlineKeyboardMarkup | None:
    # Создаем кнопки
    button_prev = InlineKeyboardButton(text="Назад", callback_data="history_command_prev_button")
    button_next = InlineKeyboardButton(text="Вперёд", callback_data="history_command_next_button")

    # Проверяем случай с пустыми результатами
    if is_empty:
        if page_number > 1:
            # Создаем клавиатуру с одной кнопкой "Назад"
            return InlineKeyboardMarkup(inline_keyboard=[[button_prev]])
        else:
            return None

    # Обрабатываем остальные случаи
    if page_number > 1:
        if need_next:
            # Кнопки "Назад" и "Вперёд"
            return InlineKeyboardMarkup(inline_keyboard=[[button_prev, button_next]])
        else:
            # Только кнопка "Назад"
            return InlineKeyboardMarkup(inline_keyboard=[[button_prev]])
    else:
        if need_next:
            # Только кнопка "Вперёд"
            return InlineKeyboardMarkup(inline_keyboard=[[button_next]])
        else:
            return None
