import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from bot.database.models import ServerAccess
from bot.utils.ssh import SshServer

LIST_CALLBACK_DATA = [
    "server:get:",
    "server:info:",
    "server:ping:",
    "server:systemctl:",
    "server:menu_user:",
    "systemctl:get:",
    "systemctl:logs:",
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

        state_data = await data["state"].get_data()

        if not any(event.data.startswith(callback_data) for callback_data in LIST_CALLBACK_DATA):
            return await handler(event, data)

        if state_data.get("ssh_server") is not None:
            ssh_server = state_data.get("ssh_server")
        else:
            server_id = None
            for callback_data in LIST_CALLBACK_DATA:
                if event.data.startswith(callback_data):
                    server_id = event.data.removeprefix(callback_data).split(":")[0]
                    break

            server_access = ServerAccess.get_or_none(server_id=server_id, user_id=event.from_user.id)

            if server_access is None:
                return await event.answer(text="Данный сервер не найден")

            await event.answer(text="Идёт подключение к серверу", show_alert=True)

            ssh_server = SshServer(server=server_access.server)

            if ssh_server.ssh_server is None:
                await asyncio.sleep(2.5)

        data["ssh_server"]: SshServer = ssh_server
        await data["state"].update_data(ssh_server=ssh_server)

        return await handler(event, data)
