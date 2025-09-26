from aiogram import Router

from . import (
    delete_server,
    menu,
    transfer_server,
    update_ip_address,
    update_name,
    update_private_key,
    update_username,
)


def register_routers():
    router = Router(name="Client ssh server settings routers")
    router.include_routers(
        delete_server.router,
        menu.router,
        update_name.router,
        update_ip_address.router,
        update_username.router,
        update_private_key.router,
        transfer_server.router,
    )
    return router


__all__ = [
    "delete_server",
    "menu",
    "transfer_server",
    "update_ip_address",
    "update_name",
    "update_private_key",
    "update_username",
]
