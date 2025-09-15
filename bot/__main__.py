import asyncio

from aiogram import Bot, F

import structlog
from structlog.typing import FilteringBoundLogger

from bot.database.models import init_db
from bot.handlers import client
from bot.middlewares import UsersMiddleware
from logs import get_structlog_config

logger: FilteringBoundLogger = structlog.get_logger()


async def on_startup(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    bot_me = await bot.me()
    await logger.ainfo("--> Username: %s", bot_me.username)


async def main():
    from config import dp, bot

    dp.message.outer_middleware(UsersMiddleware())
    dp.callback_query.outer_middleware(UsersMiddleware())

    dp.message.filter(F.chat.type == "private")

    dp.include_routers(
        client.register_routers(),
    )

    dp.startup.register(on_startup)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    structlog.configure(**get_structlog_config())

    try:
        logger.info("Starting bot")
        init_db()
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exit")
