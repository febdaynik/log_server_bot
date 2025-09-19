from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.utils.ssh import SshServer


class DisconnectServerState(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:

        state_data = await data["state"].get_data()
        ssh_server: SshServer = state_data.get("ssh_server")

        if ssh_server is not None:
            await ssh_server.disconnect()

        return await handler(event, data)
