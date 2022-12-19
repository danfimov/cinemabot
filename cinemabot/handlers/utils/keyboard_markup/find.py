from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
