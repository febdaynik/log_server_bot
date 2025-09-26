import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.client.ssh_server.settings.menu import template_menu_settings_server
from bot.keyboards.default import back_markup
from bot.utils.ssh import SshServer
from states import UpdateIPServer

router = Router()


@router.callback_query(F.data.startswith("settings:ip_address:"))
async def update_ip_address_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    msg = await call.message.edit_text(
        text="<b>Редактирование IP сервера</b>\n\n"
             f"<b>Текущий IP:</b> <code>{ssh_server.server.ip_address}</code>\n\n"
             "Введите новый IP сервера",
        reply_markup=back_markup(callback_data=f"server:settings:{ssh_server.server.id}"),
    )

    await state.set_state(UpdateIPServer.ip_address)
    return await state.update_data(msg=msg, ssh_server=ssh_server)


@router.message(UpdateIPServer.ip_address)
async def UpdateIPServer_ip_address_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    ip_address = message.text

    if not re.match(r"([0-9]{1,3}[\.]){3}[0-9]{1,3}", ip_address):
        msg = await message.answer(text="Данное значение не является IP адресом", reply_markup=data["msg"].reply_markup)
        return await state.update_data(msg=msg)

    data["ssh_server"].server.ip_address = ip_address
    data["ssh_server"].server.save()

    await state.clear()
    return await template_menu_settings_server(message=message, ssh_server=data["ssh_server"])

