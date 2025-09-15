import asyncssh
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.database.models import Server, ServerAccess
from bot.keyboards.systemctl import list_services_markup
from bot.utils.systemctl import parse_systemctl_output

router = Router()


async def get_list_services_ssh_server(server: Server) -> str:
    private_key = asyncssh.import_private_key(server.ssh_key)

    async with asyncssh.connect(
        server.ip_address,
        port=22,
        username=server.username,
        client_keys=[private_key],
        known_hosts=None,
    ) as conn:
        result = await conn.run("systemctl list-units --type=service --no-pager", check=False)
        return result.stdout.strip() or result.stderr.strip()


@router.callback_query(F.data.startswith("server:systemd:"))
async def get_list_services_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id = call.data.removeprefix("server:systemd:")
    server_access = ServerAccess.get_or_none(server_id=server_id, user_id=call.from_user.id)

    if server_access is None:
        return await call.answer("Данный сервер не найден")

    systemd_services = await get_list_services_ssh_server(server=server_access.server)
    services = await parse_systemctl_output(systemd_services)

    return await call.message.edit_text(
        text="<b>Список сервисов SystemD</b>\n\n"
             "<blockquote>Часть из сервисов системные, поэтому трогайте на свой страх и риск</blockquote>",
        reply_markup=list_services_markup(server_id=server_id, services=services),
    )
