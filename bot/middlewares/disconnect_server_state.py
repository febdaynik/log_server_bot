from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from configreader import ssh_manager


class DisconnectServerState(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:

        user_id = event.from_user.id

        if ssh_manager.has_connection(user_id=user_id):
            await ssh_manager.disconnect(user_id=user_id)

        return await handler(event, data)
