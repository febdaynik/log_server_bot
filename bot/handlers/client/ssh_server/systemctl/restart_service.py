from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.handlers.client.ssh_server.systemctl.get_info import template_info_service_by_ssh_server
from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("systemctl:restart:"))
async def restart_service_systemctl_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, service_name = call.data.removeprefix("systemctl:restart:").split(":")

    info_restart = await ssh_server.restart_service(service=service_name)
    print(info_restart)

    if isinstance(info_restart, dict):
        return await call.answer(text=info_restart.get("error"))

    return await template_info_service_by_ssh_server(call, ssh_server=ssh_server, service_name=service_name)
