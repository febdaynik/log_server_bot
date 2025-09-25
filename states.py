from aiogram.fsm.state import State, StatesGroup


class AddServer(StatesGroup):
    name = State()
    ip_address = State()
    ssh_key = State()


class AddUserByServer(StatesGroup):
    user_id = State()


class TerminalByServer(StatesGroup):
    command = State()
