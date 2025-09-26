import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.client.ssh_server.settings.menu import template_menu_settings_server
from bot.keyboards.default import back_markup
from bot.utils.ssh import SshServer
from states import UpdateUsernameServer

router = Router()


@router.callback_query(F.data.startswith("settings:username:"))
async def update_username_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    msg = await call.message.edit_text(
        text="<b>Редактирование username пользователя сервера</b>\n\n"
             f"<b>Текущий username:</b> <code>{ssh_server.server.username}</code>\n\n"
             "Введите новый username пользователя сервера",
        reply_markup=back_markup(callback_data=f"server:settings:{ssh_server.server.id}"),
    )

    await state.set_state(UpdateUsernameServer.username)
    return await state.update_data(msg=msg, ssh_server=ssh_server)


@router.message(UpdateUsernameServer.username)
async def UpdateUsernameServer_username_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    data["ssh_server"].server.username = message.text
    data["ssh_server"].server.save()

    await state.clear()
    return await template_menu_settings_server(message=message, ssh_server=data["ssh_server"])

