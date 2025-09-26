from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models import User, ServerAccess
from bot.handlers.client.start import template_send_welcome
from bot.keyboards.default import back_markup
from bot.keyboards.settings_server import confirm_transfer_server_markup
from bot.utils.ssh import SshServer
from states import TransferServer

router = Router()


@router.callback_query(F.data.startswith("server:transfer:confirm:"), TransferServer.confirm)
async def confirm_transfer_server_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    data = await state.get_data()

    if not data["user_with_access"]:
        ServerAccess.create(user_id=data["user_id"], server=ssh_server.server)

    ssh_server.server.owner_id = data["user_id"]
    ssh_server.server.save()

    return await template_send_welcome(message=call)


@router.callback_query(F.data.startswith("server:transfer:"))
async def transfer_server_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    msg = await call.message.edit_text(
        text="Укажите идентификатор пользователя, которому хотите отдать сервер\n\n"
             "<blockquote>При этом у вас останется доступ к серверу, но без доп.функций</blockquote>",
        reply_markup=back_markup(callback_data=f"server:settings:{ssh_server.server.id}"),
    )

    await state.set_state(TransferServer.user_id)
    return await state.update_data(msg=msg, ssh_server=ssh_server)


@router.message(TransferServer.user_id)
async def TransferServer_user_id_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    user_id = message.text

    if not user_id.isdigit():
        msg = await message.answer(
            text="ID пользователя должно быть указано числом",
            reply_markup=data["msg"].reply_markup,
        )
        return await state.update_data(msg=msg)

    user = User.get_or_none(user_id=user_id)
    if user is None:
        msg = await message.answer(
            text="Данный пользователь не найден\n\n"
                 "Кажется, данный пользователь не является участником бота\n"
                 "Попробуйте указать другой идентификатор",
            reply_markup=data["msg"].reply_markup,
        )
        return await state.update_data(msg=msg)

    server_access = ServerAccess.get_or_none(user=user, server=data["ssh_server"].server)
    user_with_access = bool(server_access)

    msg = await message.answer(
        text="Вы уверены, что хотите передать доступ данному пользователю?",
        reply_markup=confirm_transfer_server_markup(server_id=data["ssh_server"].server.id)
    )
    await state.set_state(TransferServer.confirm)
    return await state.update_data(msg=msg, user_with_access=user_with_access, user_id=user_id, user=user)
