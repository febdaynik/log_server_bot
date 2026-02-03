from aiogram import Router

from . import (
    download_logs,
    get_info,
    get_logs,
    list_containers,
    restart_container,
)


def register_routers():
    router = Router(name="Client ssh server docker routers")
    router.include_routers(
        download_logs.router,
        get_info.router,
        get_logs.router,
        list_containers.router,
        restart_container.router,
    )
    return router


__all__ = [
    "download_logs",
    "get_info",
    "get_logs",
    "list_containers",
    "restart_container",
]
