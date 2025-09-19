from aiogram import Router

from . import (
    add_user,
    delete_user,
    menu,
)


def register_routers():
    router = Router(name="Client ssh server user routers")
    router.include_routers(
        add_user.router,
        delete_user.router,
        menu.router,
    )
    return router


__all__ = [
    "add_user",
    "delete_user",
    "menu",
]
