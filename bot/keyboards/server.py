from aiogram.utils.keyboard import InlineKeyboardBuilder


def server_info_markup(server_id: int) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(text="🏓 Пинг", callback_data=f"server:ping:{server_id}")
    markup.button(text="ℹ Получить информацию", callback_data=f"server:info:{server_id}")
    markup.button(text="📋 Сервисы (systemd)", callback_data=f"server:systemctl:{server_id}")
    markup.button(text="💬 Терминал", callback_data=f"server:terminal:{server_id}")
    markup.button(text="🫂 Пользователи", callback_data=f"server:menu_user:{server_id}")
    markup.button(text="« Назад", callback_data="menu:start")
    markup.adjust(1)

    return markup.as_markup()


def terminal_markup(server_id: int) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(text="Попробовать ещё раз", callback_data=f"server:ping:{server_id}")
    markup.button(text="« Назад", callback_data=f"server:get:{server_id}")
    markup.adjust(1)

    return markup.as_markup()
