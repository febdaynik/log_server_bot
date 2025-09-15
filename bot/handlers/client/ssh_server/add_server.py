from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models import Server, ServerAccess
from bot.handlers.client.start import template_send_welcome
from bot.keyboards.default import back_markup
from states import AddServer

router = Router()


@router.callback_query(F.data == "menu:add_server")
async def add_server_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    msg = await call.message.edit_text(
        text="Укажите название сервера, чтобы не потерять его в списке",
        reply_markup=back_markup(),
    )

    await state.set_state(AddServer.name)
    return await state.update_data(msg=msg)


@router.message(AddServer.name)
async def AddServer_name_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    msg = await message.answer(text="Теперь введите IP адрес сервера", reply_markup=data["msg"].reply_markup)

    await state.update_data(msg=msg, name=message.text)
    return await state.set_state(AddServer.ip_address)


@router.message(AddServer.ip_address)
async def AddServer_ip_address_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    msg = await message.answer(
        text="<b>Создание SSH Private Key</b>\n\n"
             "1. Проверьте настройку SSH <code>cat /etc/ssh/sshd_config</code> \n"
             "(должно быть так: \nPubkeyAuthentication yes\nPasswordAuthentication yes; без #)\n\n"
             "1.2 Если данные параметры указаны no или закомментированы, то исправьте это\n\n"
             "2. Создаём ключ (RSA или ED-25519) <code>ssh-keygen -t rsa</code> или "
             "<code>ssh-keygen -t ed_25519</code>\n\n"
             "3. У вас появятся два файл. Откройте файл с расширением .pub и укажите в .ssh/authorized_keys то, "
             "что указано в том файле\n\n"
             "Теперь пришлите мне содержимое файла без расширения .pub",
        reply_markup=data["msg"].reply_markup,
    )

    await state.update_data(msg=msg, ip_address=message.text)
    return await state.set_state(AddServer.ssh_key)


@router.message(AddServer.ssh_key)
async def AddServer_ssh_key_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_reply_markup()

    server = Server.create(name=data["name"], ip_address=data["ip_address"], ssh_key=message.text)
    ServerAccess.create(user=message.from_user.id, server=server)

    await state.clear()
    return await template_send_welcome(message=message)
