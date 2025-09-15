import asyncio
from contextlib import suppress

import asyncssh
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.database.models import Server, ServerAccess
from bot.keyboards.server import server_info_markup

router = Router()


async def get_info_ssh_server(server: Server) -> str:
    info = dict()
    commands = {
        "OS": "uname -a",
        "Uptime": "uptime -p",
        "Disk": "df -h --total | grep total",
        "Memory": "free -m"
    }

    private_key = asyncssh.import_private_key(server.ssh_key)

    async with asyncssh.connect(
        server.ip_address,
        port=22,
        username=server.username,
        client_keys=[private_key],
        known_hosts=None,
    ) as conn:
        tasks = {k: conn.run(cmd, check=False) for k, cmd in commands.items()}
        results = await asyncio.gather(*tasks.values())

        for (k, _), result in zip(tasks.items(), results):
            info[k] = result.stdout.strip() or result.stderr.strip()

    return (
        f"<b>OS:</b> {info.get('OS')}\n"
        f"<b>Uptime:</b> {info.get('Uptime')}\n"
        f"<b>Disk:</b> {info.get('Disk')}\n"
        f"<b>Memory:</b> {info.get('Memory')}"
    )


@router.callback_query(F.data.startswith("server:get:"))
async def get_server_info_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id = call.data.removeprefix("server:get:")
    server_access = ServerAccess.get_or_none(server_id=server_id, user_id=call.from_user.id)

    if server_access is None:
        return await call.answer("Данный сервер не найден")

    with suppress(TelegramBadRequest):
        msg = await call.message.edit_text(
            "<b>Информация о сервере</b>\n\n"
            f"<b>Название:</b> {server_access.server.name}\n"
            f"<b>IP:</b> <code>{server_access.server.ip_address}</code>\n"
            f"<b>OS:</b> 🔄\n"
            f"<b>Uptime:</b> 🔄\n"
            f"<b>Disk:</b> 🔄\n"
            f"<b>Memory:</b> 🔄\n\n"
            "<blockquote>Ожидайте, идёт получение информации с сервера...</blockquote>\n\n"
            "<blockquote>Выполнение команд занимает некоторое время</blockquote>",
            reply_markup=server_info_markup(server_id=server_id),
        )

    get_info = await get_info_ssh_server(server=server_access.server)

    with suppress(TelegramBadRequest):
        return await msg.edit_text(
            text="<b>Информация о сервере</b>\n\n"
                 f"<b>Название:</b> {server_access.server.name}\n"
                 f"<b>IP:</b> <code>{server_access.server.ip_address}</code>\n"
                 f"{get_info}\n\n"
                 "<blockquote>Выполнение команд занимает некоторое время</blockquote>",
            reply_markup=server_info_markup(server_id=server_id),
        )

    return await call.answer("Изменений не найдено")
