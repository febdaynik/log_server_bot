from io import BytesIO

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile

from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("docker:download_logs:"))
async def download_docker_container_logs_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, container_id = call.data.removeprefix("docker:download_logs:").split(":")

    full_logs = await ssh_server.get_full_logs_docker_container(container_id=container_id)
    if isinstance(full_logs, dict):
        return await call.answer(text=full_logs.get("error"))

    bio = BytesIO(full_logs.encode("utf-8"))

    return await call.message.answer_document(
        document=BufferedInputFile(file=bio.getvalue(), filename=f"docker_container_{container_id}_logs.txt")
    )
