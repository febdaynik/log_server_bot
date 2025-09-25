import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from bot.database.models import ServerAccess
from configreader import ssh_manager

LIST_CALLBACK_DATA = [
    "server:get:",
    "server:info:",
    "server:ping:",
    "server:systemctl:",
    "server:menu_user:",
    "server:terminal:",
    "systemctl:get:",
    "systemctl:logs:",
    "systemctl:download_logs:",
    "systemctl:restart:",
    "user:add:",
    "user:del:",
]


class ServerStateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:

        # если callback не относится к SSH — пропускаем
        if not any(event.data.startswith(callback_data) for callback_data in LIST_CALLBACK_DATA):
            return await handler(event, data)

        # достаём server_id из callback
        server_id = None
        for callback_data in LIST_CALLBACK_DATA:
            if event.data.startswith(callback_data):
                server_id = event.data.removeprefix(callback_data).split(":")[0]
                break

        if not server_id:
            return await event.answer("Не удалось определить сервер")

        # проверяем доступ
        server_access = ServerAccess.get_or_none(server_id=server_id, user_id=event.from_user.id)
        if server_access is None:
            return await event.answer("Данный сервер не найден")

        # проверяем, есть ли уже подключение
        if ssh_manager.has_connection(event.from_user.id):
            conn = await ssh_manager.get_connection(
                user_id=event.from_user.id,
                server=server_access.server,
            )
        else:
            await event.answer("Подключение к серверу...", show_alert=True)
            conn = await ssh_manager.get_connection(
                user_id=event.from_user.id,
                server=server_access.server,
            )

            if conn.ssh_server is None:
                await asyncio.sleep(2.0)

        data["ssh_server"] = conn

        return await handler(event, data)