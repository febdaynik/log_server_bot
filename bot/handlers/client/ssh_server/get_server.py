from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.server import server_info_markup
from bot.utils.ssh import SshServer

router = Router()


async def template_get_server(call: CallbackQuery, ssh_server: SshServer) -> Message:
    is_connected = ssh_server.is_connected
    is_owner = ssh_server.server.owner_id == call.from_user.id

    if is_connected:
        blockquote = (
            "<blockquote>Нажмите кнопку \"Получить информацию\", чтобы информация обновилась\n\n"
            "Это сделано для того, чтобы бот не зависал</blockquote>"
        )
    else:
        blockquote = (
            "<blockquote>Чтобы взаимодействовать с сервером необходимо подключиться\n\n"
            "Для подключения нажмите на кнопку \"Подключиться\"</blockquote>"
        )

    return await call.message.edit_text(
        "<b>Информация о сервере</b>\n\n"
        f"<b>Название:</b> {ssh_server.server.name}\n"
        f"<b>IP:</b> <code>{ssh_server.server.ip_address}</code>\n"
        "<b>🖥 OS:</b> <i>По запросу</i>\n"
        "<b>⏰ Время работы:</b> <i>По запросу</i>\n"
        "<b>💽 Диск:</b> <i>По запросу</i>\n"
        "<b>💾 Память:</b> <i>По запросу</i>\n\n"
        f"{blockquote}",
        reply_markup=server_info_markup(server_id=ssh_server.server.id, is_connected=is_connected, is_owner=is_owner),
    )


@router.callback_query(F.data.startswith("server:get:"))
async def get_server_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    return await template_get_server(call=call, ssh_server=ssh_server)
