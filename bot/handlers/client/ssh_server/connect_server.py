from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.handlers.client.ssh_server.get_server import template_get_server
from bot.utils.ssh import SshServer

router = Router()


@router.callback_query(F.data.startswith("server:connect:"))
async def connect_server_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    """
    Данная функция является оболочкой для подключения к ssh серверу
    Всё подключение происходит в middleware ServerStateMiddleware

    :param call: CallbackQuery
    :param state: FSMContext
    :param ssh_server: SshServer
    :return:
    """

    await state.clear()

    return await template_get_server(call=call, ssh_server=ssh_server)
