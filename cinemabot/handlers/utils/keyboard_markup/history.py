from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def construct_keyboard_markup_for_history(
    page_number: int,
    is_empty: bool,
    need_next: bool,
) -> InlineKeyboardMarkup | None:
    keyboard_markup = InlineKeyboardMarkup()
    button_prev = InlineKeyboardButton("Назад", callback_data="history_command_prev_button")
    button_next = InlineKeyboardButton("Вперёд", callback_data="history_command_next_button")

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
