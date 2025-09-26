from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder


def server_info_markup(
    server_id: int,
    is_connected: bool,
    is_owner: Optional[bool] = False,
) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    if is_connected:
        markup.button(text="🏓 Пинг", callback_data=f"server:ping:{server_id}")
        markup.button(text="📋 Сервисы (systemd)", callback_data=f"server:systemctl:{server_id}")
        markup.button(text="ℹ Получить информацию", callback_data=f"server:info:{server_id}")
    else:
        markup.button(text="📶 Подключиться", callback_data=f"server:connect:{server_id}")

    if is_owner:
        markup.button(text="🫂 Пользователи", callback_data=f"server:menu_user:{server_id}")
        markup.button(text="⚙ Настройки", callback_data=f"server:settings:{server_id}")

    markup.button(text="« Назад", callback_data="menu:start")
    markup.adjust(1)

    return markup.as_markup()


