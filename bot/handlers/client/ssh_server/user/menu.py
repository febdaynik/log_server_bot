from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models import ServerAccess
from bot.keyboards.user_by_server import menu_user_by_server_markup

router = Router()


async def template_menu_user_by_server(call: CallbackQuery, server_id: int) -> Message:
    users = ServerAccess.select().where(ServerAccess.server_id == server_id)

    with suppress(TelegramBadRequest):
        return await call.message.edit_text(
            text="<b>Список добавленных пользователей</b>\n\n"
                 "<blockquote>Для того, чтобы лишить пользователя доступа к серверу, нажмите на него</blockquote>",
            reply_markup=menu_user_by_server_markup(users=users, server_id=server_id),
        )
    return await call.answer("Изменений не найдено")


@router.callback_query(F.data.startswith("server:menu_user:"))
async def menu_user_by_server_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id = call.data.removeprefix("server:menu_user:")

    return await template_menu_user_by_server(call=call, server_id=server_id)
