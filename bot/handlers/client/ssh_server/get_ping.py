from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("server:ping:"))
async def get_ping_callback(call: CallbackQuery, ssh_server: SshServer):
    ping = await ssh_server.get_ping()

    return await call.answer(f"Сервер жив: {ping}")
