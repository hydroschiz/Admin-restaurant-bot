from typing import Union

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from restbot_config import get_admins


class IsRestbotAdmin(Filter):
    """Checking if a user is an administrator"""

    def __init__(self) -> None:
        pass

    async def __call__(self, query_or_message: Union[Message, CallbackQuery]) -> bool:
        return str(query_or_message.from_user.id) in get_admins()
