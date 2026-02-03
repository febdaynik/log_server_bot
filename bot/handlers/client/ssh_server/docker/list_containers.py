from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.docker import list_containers_markup
from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("server:docker:"))
async def get_list_containers_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    containers = await ssh_server.get_list_docker_containers()

    if isinstance(containers, str):
        return await call.answer(text=containers)

    return await call.message.edit_text(
        text="<b>Список Docker контейнеров</b>",
        reply_markup=list_containers_markup(server_id=ssh_server.server.id, containers=containers),
    )
