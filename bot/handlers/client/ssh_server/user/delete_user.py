from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.database.models import ServerAccess
from bot.handlers.client.ssh_server.user.menu import template_menu_user_by_server

router = Router()


@router.callback_query(F.data.startswith("user:del:"))
async def add_user_by_server_callback(call: CallbackQuery):
    server_id, user_id = call.data.removeprefix("user:del:").split(":")

    if int(user_id) == call.from_user.id:
        return await call.answer(text="Вы не можете лишить себя доступа")

    ServerAccess.delete().where(ServerAccess.server_id == server_id, ServerAccess.user_id == user_id).execute()

    return await template_menu_user_by_server(call=call, server_id=server_id)
