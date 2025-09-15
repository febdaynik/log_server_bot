import asyncssh
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.database.models import Server, ServerAccess
from bot.handlers.client.ssh_server.systemctl.get_info import template_info_service_by_ssh_server

router = Router()


async def restart_service_by_ssh_server(server: Server, service: str) -> str:
    private_key = asyncssh.import_private_key(server.ssh_key)

    async with asyncssh.connect(
        server.ip_address,
        port=22,
        username=server.username,
        client_keys=[private_key],
        known_hosts=None,
    ) as conn:
        result = await conn.run(f"systemctl restart {service}.service", check=False)
        return result.stdout.strip() or result.stderr.strip()


@router.callback_query(F.data.startswith("systemctl:restart:"))
async def restart_service_systemctl_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id, service_name = call.data.removeprefix("systemctl:restart:").split(":")
    server_access = ServerAccess.get_or_none(server_id=server_id, user_id=call.from_user.id)

    if server_access is None:
        return await call.answer("Данный сервер не найден")

    info_restart = await restart_service_by_ssh_server(server=server_access.server, service=service_name)

    print(info_restart)

    return await template_info_service_by_ssh_server(call, server_id=server_id, service_name=service_name)
