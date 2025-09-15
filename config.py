import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage


# Данные для бота и апи
TOKEN_BOT: str = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN_BOT, default=DefaultBotProperties(parse_mode="html"))
dp = Dispatcher(storage=MemoryStorage())
