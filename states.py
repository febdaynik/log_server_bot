from aiogram.fsm.state import State, StatesGroup


class AddServer(StatesGroup):
    name = State()
    ip_address = State()
    ssh_key = State()


class AddUserByServer(StatesGroup):
    user_id = State()


class UpdateNameServer(StatesGroup):
    name = State()


class UpdateIPServer(StatesGroup):
    ip_address = State()


class UpdateUsernameServer(StatesGroup):
    username = State()


class UpdatePrivateKeyServer(StatesGroup):
    private_key = State()


class TransferServer(StatesGroup):
    user_id = State()
    confirm = State()
