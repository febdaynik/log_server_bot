from typing import Union

from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models import Server, ServerAccess
from bot.keyboards.default import start_markup
from bot.middlewares import DisconnectServerState

router = Router()
router.callback_query.outer_middleware(DisconnectServerState())


async def template_send_welcome(message: Union[Message, CallbackQuery]):
    servers = Server.select().join(ServerAccess).where(ServerAccess.user_id == message.from_user.id)

    text = (
        "👋 Приветствую, я бот для просмотра важной информации на серверах\n\n"
        f"<b>Количество серверов:</b> {len(servers)} шт.\n\n"
        "Нажмите кнопку <b>\"➕ Добавить сервер\"</b>, чтобы добавить новый сервер или выбери желаемый"
    )

    reply_markup = start_markup(servers=servers)

    if isinstance(message, CallbackQuery):
        return await message.message.edit_text(text=text, reply_markup=reply_markup)

    return await message.answer(text=text, reply_markup=reply_markup)


@router.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    """
        Обработчик команды /start на случай
    """
    await state.clear()
    return await template_send_welcome(message)


@router.callback_query(F.data == "menu:start")
async def send_welcome_callback(message: Message, state: FSMContext):
    await state.clear()
    return await template_send_welcome(message)
