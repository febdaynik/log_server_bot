import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.client.ssh_server.settings.menu import template_menu_settings_server
from bot.keyboards.default import back_markup
from bot.utils.ssh import SshServer
from states import UpdatePrivateKeyServer

router = Router()


@router.callback_query(F.data.startswith("settings:private_key:"))
async def update_private_key_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    msg = await call.message.edit_text(
        text="<b>Редактирование SSH Private Key</b>\n\n"
             f"<b>Текущий Private Key:</b> <blockquote>{ssh_server.server.ssh_key}</blockquote>\n\n"
             "Введите новый SSH Private Key",
        reply_markup=back_markup(callback_data=f"server:settings:{ssh_server.server.id}"),
    )

    await state.set_state(UpdatePrivateKeyServer.private_key)
    return await state.update_data(msg=msg, ssh_server=ssh_server)


@router.message(UpdatePrivateKeyServer.private_key)
async def UpdatePrivateKeyServer_private_key_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    pattern = re.compile(
        r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----\s+"
        r"([A-Za-z0-9+/=\s]+)"
        r"-----END (?:RSA |DSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----",
        re.DOTALL
    )
    private_key = message.text

    if not pattern.match(private_key):
        msg = await message.answer(
            text="Данное значение не является SSH Private Key",
            reply_markup=data["msg"].reply_markup,
        )
        return await state.update_data(msg=msg)

    data["ssh_server"].server.ssh_key = private_key
    data["ssh_server"].server.save()

    await state.clear()
    return await template_menu_settings_server(message=message, ssh_server=data["ssh_server"])

