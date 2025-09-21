from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.text_decorations import html_decoration as html

from bot.keyboards.systemctl import service_logs_markup
from bot.utils.ssh import SshServer

router = Router()


async def template_get_service_systemctl_logs(
    call: CallbackQuery,
    ssh_server: SshServer,
    server_id: int,
    service_name: str,
    page: int = 1,
):
    print("maw")

    info_logs = await ssh_server.get_logs_service(service=service_name, page=page)

    print("LOGI", info_logs)

    logs = info_logs.get("logs")

    if len(logs) > 4000:
        last_logs_index = len(logs) - 4000
        logs = "...\n\n" + logs[last_logs_index:len(logs)]

    return await call.message.edit_text(
        text=f"<b>Логи сервиса:</b> <code>{service_name}</code>\n\n"
             f'<pre><code class="language-shell">{html.quote(logs)}</code></pre>',
        reply_markup=service_logs_markup(
            server_id=server_id,
            service_name=service_name,
            page=info_logs["page"],
            total_pages=info_logs["total_pages"]
        ),
    )


@router.callback_query(F.data.startswith("systemctl:logs:next:"))
@router.callback_query(F.data.startswith("systemctl:logs:back:"))
async def get_service_systemctl_logs_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, service_name, page = (call.data
                                     .removeprefix("systemctl:logs:next:")
                                     .removeprefix("systemctl:logs:back:")
                                     .split(":"))

    return await template_get_service_systemctl_logs(call, ssh_server, server_id, service_name, page=int(page))


@router.callback_query(F.data.startswith("systemctl:logs:"))
async def get_service_systemctl_logs_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, service_name = call.data.removeprefix("systemctl:logs:").split(":")
    print(service_name, server_id)

    return await template_get_service_systemctl_logs(call, ssh_server, server_id, service_name)
