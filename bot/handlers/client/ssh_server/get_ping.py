from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("server:ping:"))
async def get_ping_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    ping = await ssh_server.get_ping()

    return await call.answer(f"Сервер жив: {ping}")
