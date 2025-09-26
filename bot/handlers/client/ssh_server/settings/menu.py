from contextlib import suppress
from typing import Union

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.settings_server import menu_settings_server_markup
from bot.utils.ssh import SshServer

router = Router()


async def template_menu_settings_server(message: Union[CallbackQuery, Message], ssh_server: SshServer) -> Message:
    text = (
        "<b>Настройки</b>\n\n"
        f"<b>Название:</b> <code>{ssh_server.server.name}</code>\n"
        f"<b>IP:</b> <code>{ssh_server.server.ip_address}</code>\n"
        f"<b>Username:</b> <code>{ssh_server.server.username}</code>\n"
        f"<b>Private Key (часть):</b> <blockquote>{ssh_server.server.ssh_key[:30]} ...</blockquote>"
    )
    reply_markup = menu_settings_server_markup(server_id=ssh_server.server.id)

    if isinstance(message, CallbackQuery):
        with suppress(TelegramBadRequest):
            return await message.message.edit_text(text=text, reply_markup=reply_markup, protect_content=True)
        return await message.answer(text="Изменений не найдено")

    return await message.answer(text=text, reply_markup=reply_markup, protect_content=True)


@router.callback_query(F.data.startswith("server:settings:"))
async def menu_settings_server_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    return await template_menu_settings_server(message=call, ssh_server=ssh_server)
