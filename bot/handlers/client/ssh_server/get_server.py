from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.server import server_info_markup
from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("server:get:"))
async def get_server_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    return await call.message.edit_text(
        "<b>Информация о сервере</b>\n\n"
        f"<b>Название:</b> {ssh_server.server.name}\n"
        f"<b>IP:</b> <code>{ssh_server.server.ip_address}</code>\n"
        f"<b>OS:</b> <i>По запросу</i>\n"
        f"<b>Uptime:</b> <i>По запросу</i>\n"
        f"<b>Disk:</b> <i>По запросу</i>\n"
        f"<b>Memory:</b> <i>По запросу</i>\n\n"
        "<blockquote>Нажмите кнопку \"Получить информацию\", чтобы информация обновилась\n\n"
        "Это сделано для того, чтобы бот не зависал</blockquote>",
        reply_markup=server_info_markup(server_id=ssh_server.server.id),
    )
