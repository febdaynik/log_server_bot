from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.client.ssh_server.settings.menu import template_menu_settings_server
from bot.keyboards.default import back_markup
from bot.utils.ssh import SshServer
from states import UpdateNameServer

router = Router()


@router.callback_query(F.data.startswith("settings:name:"))
async def update_name_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    msg = await call.message.edit_text(
        text="<b>Редактирование названия сервера</b>\n\n"
             f"<b>Текущее название:</b> <code>{ssh_server.server.name}</code>\n\n"
             "Введите новое название сервера",
        reply_markup=back_markup(callback_data=f"server:settings:{ssh_server.server.id}"),
    )

    await state.set_state(UpdateNameServer.name)
    return await state.update_data(msg=msg, ssh_server=ssh_server)


@router.message(UpdateNameServer.name)
async def UpdateNameServer_name_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    data["ssh_server"].server.name = message.text
    data["ssh_server"].server.save()

    await state.clear()
    return await template_menu_settings_server(message=message, ssh_server=data["ssh_server"])

