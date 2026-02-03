from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.default import back_markup
from bot.keyboards.docker import container_info_markup
from bot.keyboards.systemctl import service_info_markup
from bot.utils.ssh import SshServer

router = Router()


async def template_info_container_by_ssh_server(call: CallbackQuery, ssh_server: SshServer, container_id: str):
    info_container = await ssh_server.get_info_docker_container(container_id=container_id)

    if isinstance(info_container, str):
        return await call.answer(text=info_container)

    if isinstance(info_container, dict):
        return await call.answer(text=info_container.get("error"))

    info_container = info_container[0]

    config_container = info_container.get("Config", {})
    command_start = " ".join(config_container.get("Cmd", []) or [])

    state_container = info_container.get("State", {})
    status_container = (
        "Запущен"
        if state_container.get("Running", False)
        else "На паузе"
        if state_container.get("Paused", False)
        else "Перезапускается"
        if state_container.get("Restarting", False)
        else "Остановлен"
    )
    error_container = (
        f"<b>Код ошибки:</b> {state_container.get('ExitCode')}\n"
        f"<b>Ошибка:</b> <blockquote>{state_container.get('Error')}</blockquote>\n"
        if state_container.get("Error", False)
        else ""
    )

    with suppress(TelegramBadRequest):
        return await call.message.edit_text(
            text=f"<b>Информация о Docker контейнере:</b> <code>{info_container.get('Name')}</code>\n\n"
                 f"<b>ID:</b> {info_container.get('Id')}\n"
                 f"<b>Команда запуска:</b> <code>{command_start}</code>\n"
                 f"<b>Драйвер:</b> {info_container.get('Driver')}\n"
                 f"<b>Платформа:</b> {info_container.get('Platform')}\n\n"
                 f"<b>Образ:</b> {config_container.get('Image')}\n"
                 f"<b>Рабочая директория:</b> {config_container.get('WorkingDir')}\n\n"
                 f"<b>PID:</b> {state_container.get('Pid')}\n"
                 f"<b>Статус:</b> {state_container.get('Status')}\n"
                 f"<b>Состояние:</b> {status_container}\n"
                 f"{error_container}\n",
                 # f"<b>Используемая память:</b> {json_info_service.get('MemoryCurrent')} байт\n",
            reply_markup=container_info_markup(server_id=ssh_server.server.id, container_id=container_id),
        )


@router.callback_query(F.data.startswith("docker:get:"))
async def get_docker_container_info_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, container_id = call.data.removeprefix("docker:get:").split(":")

    return await template_info_container_by_ssh_server(call=call, ssh_server=ssh_server, container_id=container_id)
