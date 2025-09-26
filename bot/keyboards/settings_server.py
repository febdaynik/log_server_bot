from aiogram.utils.keyboard import InlineKeyboardBuilder


def menu_settings_server_markup(server_id: int) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(text="✏ Изменить название", callback_data=f"settings:name:{server_id}")
    markup.button(text="⌨ Изменить IP", callback_data=f"settings:ip_address:{server_id}")
    markup.button(text="👤 Изменить username пользователя сервера", callback_data=f"settings:username:{server_id}")
    markup.button(text="🔑 Изменить private key", callback_data=f"settings:private_key:{server_id}")
    markup.button(text="🔥 Передача права собственности", callback_data=f"server:transfer:{server_id}")
    markup.button(text="🗑 Удалить сервер", callback_data=f"server:delete:{server_id}")
    markup.button(text="« Назад", callback_data=f"server:get:{server_id}")
    markup.adjust(1)

    return markup.as_markup()


def confirm_delete_server_markup(server_id: int) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(text="✅ Подтвердить", callback_data=f"server:delete:confirm:{server_id}")
    markup.button(text="❌ Отклонить", callback_data=f"server:settings:{server_id}")
    markup.adjust(1)

    return markup.as_markup()


def confirm_transfer_server_markup(server_id: int) -> InlineKeyboardBuilder.as_markup:
    markup = InlineKeyboardBuilder()

    markup.button(text="✅ Подтвердить", callback_data=f"server:transfer:confirm:{server_id}")
    markup.button(text="❌ Отклонить", callback_data=f"server:settings:{server_id}")
    markup.adjust(1)

    return markup.as_markup()