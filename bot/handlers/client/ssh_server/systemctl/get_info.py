from contextlib import suppress

import asyncssh
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.database.models import Server, ServerAccess
from bot.keyboards.systemctl import service_info_markup

router = Router()


async def get_info_service_by_ssh_server(server: Server, service: str) -> str:
    private_key = asyncssh.import_private_key(server.ssh_key)

    async with asyncssh.connect(
        server.ip_address,
        port=22,
        username=server.username,
        client_keys=[private_key],
        known_hosts=None,
    ) as conn:
        result = await conn.run(f"systemctl status {service}.service --no-pager", check=False)
        return result.stdout.strip() or result.stderr.strip()


async def template_info_service_by_ssh_server(call: CallbackQuery, server_id: int, service_name: str):
    server_access = ServerAccess.get_or_none(server_id=server_id, user_id=call.from_user.id)

    if server_access is None:
        return await call.answer("Данный сервер не найден")

    info_service = await get_info_service_by_ssh_server(server=server_access.server, service=service_name)

    if len(info_service) > 4000:
        info_service = info_service[:4000] + "\n\n... вывод обрезан ..."

    with suppress(TelegramBadRequest):
        return await call.message.edit_text(
            text=f"<b>Статус сервиса:</b> <code>{service_name}</code>\n\n"
                 f'<pre><code class="language-shell">{info_service}</code></pre>',
            reply_markup=service_info_markup(server_id=server_id, service=service_name),
        )


@router.callback_query(F.data.startswith("systemctl:get:"))
async def get_service_systemctl_info_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id, service_name = call.data.removeprefix("systemctl:get:").split(":")

    return await template_info_service_by_ssh_server(call, server_id=server_id, service_name=service_name)
