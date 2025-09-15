from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.database.models import User


class UsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]
        ],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:

        user = User.get_or_none(user_id=event.from_user.id)

        if user is not None:
            if event.from_user.username != user.username:
                user.username = event.from_user.username

            user.save()

        else:
            user = User.create(user_id=event.from_user.id, username=event.from_user.username)

        data["user"] = user

        return await handler(event, data)
