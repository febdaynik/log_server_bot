from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.systemctl import list_services_markup
from bot.utils.ssh import SshServer
from bot.utils.systemctl import sorted_systemctl

router = Router()


@router.callback_query(F.data.startswith("server:systemctl:"))
async def get_list_services_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    systemd_services = await ssh_server.get_list_systemctl()
    if isinstance(systemd_services, str):
        return await call.answer(text=systemd_services)

    services = await sorted_systemctl(systemd_services)
    return await call.message.edit_text(
        text="<b>Список сервисов SystemD</b>\n\n"
             "<blockquote>Часть из сервисов системные, поэтому трогайте на свой страх и риск</blockquote>",
        reply_markup=list_services_markup(server_id=ssh_server.server.id, services=services),
    )
