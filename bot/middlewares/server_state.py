import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from asyncssh import PermissionDenied

from bot.database.models import ServerAccess
from configreader import ssh_manager

LIST_CALLBACK_DATA = [
    "server:get:",
    "server:connect:",
    "server:info:",
    "server:ping:",
    "server:systemctl:",
    "server:menu_user:",
    "server:settings:",
    "server:transfer:confirm:",
    "server:transfer:",
    "settings:ip_address:",
    "settings:name:",
    "settings:private_key:",
    "settings:username:",
    "systemctl:get:",
    "systemctl:logs:next:",
    "systemctl:logs:back:",
    "systemctl:logs:",
    "systemctl:download_logs:",
    "systemctl:restart:",
    "user:add:",
    "user:del:",
]

LIST_CALLBACK_DATA_NO_CONNECT_SERVER = [
    "server:get:",
    "server:menu_user:",
    "server:settings:",
    "server:transfer:confirm:",
    "server:transfer:",
    "settings:ip_address:",
    "settings:name:",
    "settings:private_key:",
    "settings:username:",
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

        user_id = event.from_user.id

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
            return await event.answer(text="Не удалось определить сервер")

        # проверяем доступ
        server_access = ServerAccess.get_or_none(server_id=server_id, user_id=user_id)
        if server_access is None:
            return await event.answer(text="Данный сервер не найден")

        # проверяем, относится ли данный callback к тем, что не нужно конектить к серверу
        if any(event.data.startswith(callback_data) for callback_data in LIST_CALLBACK_DATA_NO_CONNECT_SERVER):
            conn = await ssh_manager.get_connection(
                user_id=user_id,
                server=server_access.server,
            )
        else:
            # проверяем, есть ли уже подключение
            if ssh_manager.has_connection(user_id):
                conn = await ssh_manager.get_connection(
                    user_id=user_id,
                    server=server_access.server,
                )
            else:
                try:
                    conn = await ssh_manager.get_connection_or_create(
                        user_id=user_id,
                        server=server_access.server,
                    )
                    await event.answer(text="Подключение к серверу...", show_alert=True)

                    if conn.ssh_server is None:
                        await asyncio.sleep(2.0)
                except PermissionDenied as error:
                    return await event.answer(text=str(error))

        data["ssh_server"] = conn
        data["ssh_manager"] = ssh_manager

        return await handler(event, data)
