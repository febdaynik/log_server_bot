import asyncssh
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.database.models import Server, ServerAccess

router = Router()


async def get_ping_ssh_server(server: Server) -> str:
    private_key = asyncssh.import_private_key(server.ssh_key)

    async with asyncssh.connect(
        server.ip_address,
        port=22,
        username=server.username,
        client_keys=[private_key],
        known_hosts=None,
    ) as conn:
        result = await conn.run("uptime -p", check=False)
        return result.stdout.strip() or result.stderr.strip()


@router.callback_query(F.data.startswith("server:ping:"))
async def get_ping_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id = call.data.removeprefix("server:ping:")
    server_access = ServerAccess.get_or_none(server_id=server_id, user_id=call.from_user.id)

    if server_access is None:
        return await call.answer("Данный сервер не найден")

    ping = await get_ping_ssh_server(server=server_access.server)

    return await call.answer(f"Сервер жив: {ping}")
