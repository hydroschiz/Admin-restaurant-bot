from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from data import config
from utils.db_api.sqlite import DatabaseHelper

bot = Bot(config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db_helper = DatabaseHelper()


def get_current_message_id(admin_id):
    return db_helper.get_admin(admin_id)[1]