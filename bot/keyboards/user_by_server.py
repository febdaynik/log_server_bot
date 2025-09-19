from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import ServerAccess


def menu_user_by_server_markup(users: ServerAccess, server_id: int) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    for user in users:
        markup.button(
            text=f"🗑 {user.user.username or user.user_id}",
            callback_data=f"user:del:{server_id}:{user.user_id}",
        )

    markup.button(text="➕ Выдать доступ пользователю", callback_data=f"user:add:{server_id}")
    markup.button(text="« Назад", callback_data=f"server:get:{server_id}")
    markup.adjust(1)

    return markup.as_markup()
