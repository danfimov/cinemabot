from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def construct_keyboard_markup_for_find() -> InlineKeyboardMarkup:
    # Создаем кнопки
    button_continue = InlineKeyboardButton(text="⏭", callback_data="find_command_next_button")
    button_details = InlineKeyboardButton(text="▶️", callback_data="find_command_detail_button")
    button_stop = InlineKeyboardButton(text="⏹", callback_data="find_command_stop_button")

    # Создаем клавиатуру с кнопками в одной строке
    return InlineKeyboardMarkup(inline_keyboard=[[button_details, button_continue, button_stop]])


def construct_keyboard_markup_for_detail_view(link: str) -> InlineKeyboardMarkup:
    # Создаем кнопки
    button_with_link = InlineKeyboardButton(text="Смотреть на Кинопоиске", url=link)
    button_continue = InlineKeyboardButton(text="Следующий фильм в поиске", callback_data="find_command_next_button")

    # Создаем клавиатуру с кнопками в разных строках
    return InlineKeyboardMarkup(inline_keyboard=[[button_with_link], [button_continue]])
