from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.systemctl import list_services_markup
from bot.utils.ssh import SshServer
from bot.utils.systemctl import parse_systemctl_output

router = Router()


@router.callback_query(F.data.startswith("server:systemctl:"))
async def get_list_services_callback(call: CallbackQuery, ssh_server: SshServer):
    systemd_services = await ssh_server.get_list_systemctl()
    services = await parse_systemctl_output(systemd_services)

    return await call.message.edit_text(
        text="<b>Список сервисов SystemD</b>\n\n"
             "<blockquote>Часть из сервисов системные, поэтому трогайте на свой страх и риск</blockquote>",
        reply_markup=list_services_markup(server_id=ssh_server.server.id, services=services),
    )
