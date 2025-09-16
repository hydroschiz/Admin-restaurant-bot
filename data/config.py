from environs import Env

env = Env()
env.read_env()

# BOT_TOKEN: str = env.str("BOT_TOKEN")
ADMINS: list = env.list("ADMINS")

BOT_TOKEN = env.str('BOT_TOKEN')
HOST = env.str('HOST')
USERNAME = env.str('USERNAME')
PASSWORD = env.str('PASSWORD')

# Путь для развертывания на сервере
DEPLOY_PATH = env.str('DEPLOY_PATH')
BOT_PATH = env.str('BOT_PATH')

URL_ADD_TO_DB = env.str('URL_ADD_TO_DB')
URL_DELETE_FROM_DB = env.str('URL_DELETE_FROM_DB')
URL_EDIT_IN_DB = env.str('URL_EDIT_IN_DB')
URL_DOWNLOAD_RESTAURANTS_LIST = env.str('URL_DOWNLOAD_RESTAURANTS_LIST')

URL_INSTRUCTION = env.str('URL_INSTRUCTION')
