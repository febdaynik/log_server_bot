from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.server import server_info_markup
from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("server:info:"))
async def get_server_info_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    get_info = await ssh_server.get_info()

    with suppress(TelegramBadRequest):
        return await call.message.edit_text(
            text="<b>Информация о сервере</b>\n\n"
                 f"<b>Название:</b> {ssh_server.server.name}\n"
                 f"<b>IP:</b> <code>{ssh_server.server.ip_address}</code>\n"
                 f"{get_info}\n\n"
                 "<blockquote>Выполнение команд занимает некоторое время</blockquote>",
            reply_markup=server_info_markup(
                server_id=ssh_server.server.id,
                is_connected=ssh_server.is_connected,
                is_owner=ssh_server.server.owner_id == call.from_user.id,
            ),
        )

    return await call.answer(text="Изменений не найдено")
