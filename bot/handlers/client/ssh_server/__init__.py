from aiogram import Router

from bot.middlewares import ServerStateMiddleware
from . import (
    settings,
    systemctl,
    user,

    add_server,
    connect_server,
    get_info,
    get_ping,
    get_server,
)


def register_routers():
    router = Router(name="Client ssh server routers")

    router.callback_query.middleware(ServerStateMiddleware())

    router.include_routers(
        settings.register_routers(),
        systemctl.register_routers(),
        user.register_routers(),

        add_server.router,
        connect_server.router,
        get_info.router,
        get_ping.router,
        get_server.router,
    )
    return router


__all__ = [
    "settings",
    "systemctl",
    "user",

    "add_server",
    "connect_server",
    "get_info",
    "get_ping",
    "get_server",
]
