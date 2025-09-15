import asyncssh
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.database.models import Server, ServerAccess
from bot.keyboards.default import back_markup

router = Router()


async def get_logs_service_by_ssh_server(server: Server, service: str) -> str:
    private_key = asyncssh.import_private_key(server.ssh_key)

    async with asyncssh.connect(
        server.ip_address,
        port=22,
        username=server.username,
        client_keys=[private_key],
        known_hosts=None,
    ) as conn:
        result = await conn.run(f"journalctl -u {service}.service -n 50 --no-pager", check=False)
        return result.stdout.strip() or result.stderr.strip()


@router.callback_query(F.data.startswith("systemctl:logs:"))
async def get_service_systemctl_logs_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    server_id, service_name = call.data.removeprefix("systemctl:logs:").split(":")
    server_access = ServerAccess.get_or_none(server_id=server_id, user_id=call.from_user.id)

    if server_access is None:
        return await call.answer("Данный сервер не найден")

    logs = await get_logs_service_by_ssh_server(server=server_access.server, service=service_name)

    if len(logs) > 4000:
        info_service = logs[4000:] + "\n\n... вывод обрезан ..."

    return await call.message.edit_text(
        text=f"<b>Логи сервиса:</b> <code>{service_name}</code>\n\n"
             f'<pre><code class="language-shell">{logs}</code></pre>',
        reply_markup=back_markup(name="« Назад", callback_data=f"systemctl:get:{server_id}:{service_name}"),
    )
