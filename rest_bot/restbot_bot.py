import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import restbot_handlers
from restbot_sqlite import DatabaseRestbotHelper
from restbot_config import get_bot_token, auto_update_restbot_data

logging.basicConfig(level=logging.INFO)

restbot_bot = Bot(get_bot_token())
restbot_storage = MemoryStorage()
restbot_dp = Dispatcher(storage=restbot_storage)
restbot_db_helper = DatabaseRestbotHelper()


def on_startup():
    task_update_data = asyncio.create_task(auto_update_restbot_data())
    return task_update_data


async def main() -> None:
    restbot_dp.include_routers(
        restbot_handlers.router,
    )
    result = restbot_db_helper.create_table_users()
    if isinstance(result, Exception):
        logging.error(result)

    result = restbot_db_helper.create_table_admins()
    if isinstance(result, Exception):
        logging.error(result)

    await restbot_dp.start_polling(restbot_bot, on_startup=on_startup())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
