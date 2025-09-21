from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.systemctl import service_info_markup
from bot.utils.ssh import SshServer
from bot.utils.systemctl import translate_text_info_to_json

router = Router()


async def template_info_service_by_ssh_server(call: CallbackQuery, ssh_server: SshServer, service_name: str):
    info_service = await ssh_server.get_info_service(service=service_name)

    if isinstance(info_service, dict):
        return await call.answer(text=info_service.get("error"))

    json_info_service = await translate_text_info_to_json(info=info_service)

    with suppress(TelegramBadRequest):
        return await call.message.edit_text(
            text=f"<b>Информация о сервисе:</b> <code>{service_name}</code>\n\n"
                 f"<b>PID:</b> {json_info_service.get('MainPID')}\n"
                 f"<b>ID:</b> {json_info_service.get('Id')}\n"
                 f"<b>Используемая память:</b> {json_info_service.get('MemoryCurrent')} байт\n"
                 f"<b>Состояние загрузки конфигурации:</b> {json_info_service.get('LoadState')}\n"
                 f"<b>Основное состояние активности:</b> {json_info_service.get('ActiveState')}\n"
                 f"<b>Детальное состояние процесса:</b> {json_info_service.get('SubState')}\n"
                 f"<b>Состояние автозагрузки:</b> {json_info_service.get('UnitFileState')}\n",
            reply_markup=service_info_markup(server_id=ssh_server.server.id, service=service_name),
        )


@router.callback_query(F.data.startswith("systemctl:get:"))
async def get_service_systemctl_info_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    server_id, service_name = call.data.removeprefix("systemctl:get:").split(":")

    return await template_info_service_by_ssh_server(call=call, ssh_server=ssh_server, service_name=service_name)
