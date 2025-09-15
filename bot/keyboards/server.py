from aiogram.utils.keyboard import InlineKeyboardBuilder


def server_info_markup(server_id: int) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(text="🏓 Пинг", callback_data=f"server:ping:{server_id}")
    markup.button(text="📋 systemd", callback_data=f"server:systemd:{server_id}")
    markup.button(text="🔄 Обновить", callback_data=f"server:get:{server_id}")
    markup.button(text="➕ Выдать доступ пользователю", callback_data=f"server:add_user:{server_id}")
    markup.button(text="« Назад", callback_data="menu:start")
    markup.adjust(1)

    return markup.as_markup()
