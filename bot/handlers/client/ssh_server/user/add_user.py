from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models import ServerAccess
from bot.keyboards.default import back_markup
from bot.utils.ssh import SshServer
from states import AddUserByServer

router = Router()


@router.callback_query(F.data.startswith("user:add:"))
async def add_user_by_server_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id = call.data.removeprefix("user:add:")

    msg = await call.message.edit_text(
        text="Укажите идентификатор пользователя, которому хотите выдать доступ в боте к этому серверу",
        reply_markup=back_markup(callback_data=f"server:menu_user:{server_id}"),
    )

    await state.set_state(AddUserByServer.user_id)
    return await state.update_data(msg=msg, server_id=int(server_id), ssh_server=ssh_server)


@router.message(AddUserByServer.user_id)
async def AddUserByServer_user_id_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    user_id = message.text
    if not user_id.isdigit():
        msg = await message.answer(
            text="Идентификатор пользователя должен быть числовым значением",
            reply_markup=data["msg"].reply_markup,
        )
        return await state.update_data(msg=msg)

    ServerAccess.create(user_id=message.text, server_id=data["server_id"])

    await message.answer(text="Пользователю был выдан доступ", reply_markup=data["msg"].reply_markup)

    return state.clear()
