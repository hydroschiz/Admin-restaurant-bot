from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import admin_panel_buttons
from loader import db_helper
from states.deploy_state import Deploy

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Здравствуйте!")


@router.message(Command('admin'), IsAdmin())
async def admin(message: Message, state: FSMContext):
    bots_message = await message.answer(f"Выберите действие:",
                                        reply_markup=admin_panel_buttons)
    await state.clear()
    result = db_helper.add_admin(message.from_user.id, bots_message.message_id)
    if isinstance(result, Exception):
        result = db_helper.update_message_id_of_admin(message.from_user.id, bots_message.message_id)
    if isinstance(result, Exception):
        print(result)


# @router.message(Command('deploy'), IsAdmin())
# async def deploy(message: Message, state: FSMContext):
#     await message.answer('TESTING DEPLOY')
#     await state.set_state(Deploy.Deploy)
