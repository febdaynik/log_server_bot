from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from bot.keyboards.systemctl import service_info_markup
from bot.utils.ssh import SshServer

router = Router()


async def template_info_service_by_ssh_server(call: CallbackQuery, ssh_server: SshServer, service_name: str):
    info_service = await ssh_server.get_info_service(service=service_name)

    if len(info_service) > 4000:
        info_service = info_service[:4000] + "\n\n... вывод обрезан ..."

    with suppress(TelegramBadRequest):
        return await call.message.edit_text(
            text=f"<b>Статус сервиса:</b> <code>{service_name}</code>\n\n"
                 f'<pre><code class="language-shell">{info_service}</code></pre>',
            reply_markup=service_info_markup(server_id=ssh_server.server.id, service=service_name),
        )


@router.callback_query(F.data.startswith("systemctl:get:"))
async def get_service_systemctl_info_callback(call: CallbackQuery, ssh_server: SshServer):
    server_id, service_name = call.data.removeprefix("systemctl:get:").split(":")

    return await template_info_service_by_ssh_server(call=call, ssh_server=ssh_server, service_name=service_name)
