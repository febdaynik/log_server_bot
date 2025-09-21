from aiogram import Router

from . import (
    download_logs,
    get_info,
    get_logs,
    list_services,
    restart_service,
)


def register_routers():
    router = Router(name="Client ssh server systemctl routers")
    router.include_routers(
        get_info.router,
        get_logs.router,
        download_logs.router,
        list_services.router,
        restart_service.router,
    )
    return router


__all__ = [
    "download_logs",
    "get_info",
    "get_logs",
    "list_services",
    "restart_service",
]
