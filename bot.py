import asyncio
import logging
import sys

from handlers.users import commands, add_restaurant_handler, restaurants_list_handler
from loader import dp, db_helper, bot


async def main() -> None:
    dp.include_routers(
        commands.router,
        add_restaurant_handler.router,
        restaurants_list_handler.router,
    )
    result = db_helper.create_table_admins()
    if isinstance(result, Exception):
        logging.error(result)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
