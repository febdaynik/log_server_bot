from aiogram import Router

from . import (
    ssh_server,

    start,
)


def register_routers():
    router = Router()
    router.include_routers(
        ssh_server.register_routers(),

        start.router,
    )
    return router


__all__ = [
    "ssh_server",

    "start",
]
