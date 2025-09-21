from io import BytesIO

from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.utils.text_decorations import html_decoration as html

from bot.keyboards.systemctl import service_logs_markup
from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("systemctl:download_logs:"))
async def download_service_systemctl_logs_callback(call: CallbackQuery, ssh_server: SshServer):
    server_id, service_name = call.data.removeprefix("systemctl:download_logs:").split(":")

    full_logs = await ssh_server.get_full_logs_service(service=service_name)

    bio = BytesIO(full_logs.encode("utf-8"))

    return await call.message.answer_document(
        document=BufferedInputFile(file=bio.getvalue(), filename=f"{service_name}_logs.txt")
    )
