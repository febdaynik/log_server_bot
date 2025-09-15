from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Server


def start_markup(servers: List[Server]) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    for server in servers:
        markup.button(text=server.name, callback_data=f"server:get:{server.id}")

    markup.button(text="➕ Добавить сервер", callback_data="menu:add_server")
    markup.adjust(1)

    return markup.as_markup()


def back_markup(name: str = "Отменить", callback_data: str = "menu:start") -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()
    markup.button(text=name, callback_data=callback_data)
    return markup.as_markup()
