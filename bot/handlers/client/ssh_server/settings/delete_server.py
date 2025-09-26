from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.database.models import ServerAccess
from bot.handlers.client.start import template_send_welcome
from bot.keyboards.settings_server import confirm_delete_server_markup

router = Router()


@router.callback_query(F.data.startswith("server:delete:confirm:"))
async def confirm_delete_server_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id = call.data.removeprefix("server:delete:confirm:")

    server_access = ServerAccess.get_or_none(server_id=server_id, user_id=call.from_user.id)
    if server_access is None:
        return await call.answer(text="Данный сервер не найден")

    server_access.server.delete_instance(recursive=True)
    await call.answer(text="Сервер удалён")

    return await template_send_welcome(message=call)


@router.callback_query(F.data.startswith("server:delete:"))
async def delete_server_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id = call.data.removeprefix("server:delete:")

    return await call.message.edit_text(
        text="Вы уверены, что хотите удалить сервер?",
        reply_markup=confirm_delete_server_markup(server_id=server_id),
    )
