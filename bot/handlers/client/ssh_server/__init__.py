from aiogram import Router

from . import (
    systemctl,

    add_server,
    add_user,
    get_info,
    get_ping,
    list_services,
)


def register_routers():
    router = Router(name="Client ssh server routers")
    router.include_routers(
        systemctl.register_routers(),

        add_server.router,
        add_user.router,
        get_info.router,
        get_ping.router,
        list_services.router,
    )
    return router


__all__ = [
    "systemctl",

    "add_server",
    "add_user",
    "get_info",
    "get_ping",
    "list_services",
]
