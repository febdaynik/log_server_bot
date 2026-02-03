from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.text_decorations import html_decoration as html

from bot.keyboards.docker import container_logs_markup
from bot.utils.ssh import SshServer

router = Router()


async def template_get_docker_container_logs(
    call: CallbackQuery,
    ssh_server: SshServer,
    server_id: int,
    container_id: str,
    page: int = 1,
):
    info_logs = await ssh_server.get_logs_docker_container(container_id=container_id, page=page)

    logs = info_logs.get("logs")

    if len(logs) > 4000:
        last_logs_index = len(logs) - 4000
        logs = "...\n\n" + logs[last_logs_index:len(logs)]

    return await call.message.edit_text(
        text=f"<b>Логи контейнера с ID:</b> <code>{container_id}</code>\n\n"
             f'<pre><code class="language-shell">{html.quote(logs)}</code></pre>',
        reply_markup=container_logs_markup(
            server_id=server_id,
            container_id=container_id,
            page=info_logs["page"],
            total_pages=info_logs["total_pages"]
        ),
    )


@router.callback_query(F.data.startswith("docker:logs:next:"))
@router.callback_query(F.data.startswith("docker:logs:back:"))
async def get_service_systemctl_logs_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, container_id, page = (call.data
                                     .removeprefix("docker:logs:next:")
                                     .removeprefix("docker:logs:back:")
                                     .split(":"))

    return await template_get_docker_container_logs(call, ssh_server, server_id, container_id, page=int(page))


@router.callback_query(F.data.startswith("docker:logs:"))
async def get_docker_container_logs_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, container_id = call.data.removeprefix("docker:logs:").split(":")

    return await template_get_docker_container_logs(call, ssh_server, server_id, container_id)
