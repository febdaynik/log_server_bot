from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.default import back_markup
from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("systemctl:logs:"))
async def get_service_systemctl_logs_callback(call: CallbackQuery, ssh_server: SshServer):
    server_id, service_name = call.data.removeprefix("systemctl:logs:").split(":")

    logs = await ssh_server.get_logs_service(service=service_name)

    if len(logs) > 4000:
        last_logs_index = len(logs) - 4000
        logs = "...\n\n" + logs[last_logs_index:len(logs)]

    return await call.message.edit_text(
        text=f"<b>Логи сервиса:</b> <code>{service_name}</code>\n\n"
             f'<pre><code class="language-shell">{logs}</code></pre>',
        reply_markup=back_markup(name="« Назад", callback_data=f"systemctl:get:{server_id}:{service_name}"),
    )
