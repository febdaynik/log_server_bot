from io import BytesIO

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile

from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("systemctl:download_logs:"))
async def download_service_systemctl_logs_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, service_name = call.data.removeprefix("systemctl:download_logs:").split(":")

    full_logs = await ssh_server.get_full_logs_service(service=service_name)
    if isinstance(full_logs, dict):
        return await call.answer(text=full_logs.get("error"))

    bio = BytesIO(full_logs.encode("utf-8"))

    return await call.message.answer_document(
        document=BufferedInputFile(file=bio.getvalue(), filename=f"{service_name}_logs.txt")
    )
