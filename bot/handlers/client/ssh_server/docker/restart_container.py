from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.handlers.client.ssh_server.docker.get_info import template_info_container_by_ssh_server
from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("docker:restart:"))
async def restart_docker_container_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, container_id = call.data.removeprefix("docker:restart:").split(":")

    info_restart = await ssh_server.restart_docker_container(container_id=container_id)
    print(info_restart)

    if isinstance(info_restart, dict):
        return await call.answer(text=info_restart.get("error"))

    return await template_info_container_by_ssh_server(call, ssh_server=ssh_server, container_id=container_id)
