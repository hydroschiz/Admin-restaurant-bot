import logging
import os

import requests
from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile

from restbot_config import get_restaurant_url, get_restaurant_id, get_admins
from restbot_filters import IsRestbotAdmin
from restbot_keyboards import user_keyboard, admin_keyboard, back_button_keyboard, send_message_keyboard
from restbot_bot import restbot_db_helper, restbot_bot

router = Router()


def get_current_message_id(admin_id):
    return restbot_db_helper.get_admin(admin_id)[1]


async def download_file_to_restbot(url, file_name):

    response = requests.get(url, verify=False)

    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)

    return response


class Sending(StatesGroup):
    GetMessage = State()
    SendMessage = State()


@router.message(CommandStart())
async def command_start(message: types.Message):
    result = restbot_db_helper.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    if isinstance(result, Exception):
        result = restbot_db_helper.update_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
        )
    if isinstance(result, Exception):
        pass
    await message.answer(f'Здравствуйте, {message.from_user.first_name}',
                         reply_markup=user_keyboard)


@router.message(Command('admin'), IsRestbotAdmin())
async def command_admin(message: types.Message):
    bots_message = await message.answer(f'Здравствуйте, {message.from_user.first_name}',
                                        reply_markup=admin_keyboard)
    result = restbot_db_helper.add_admin(message.from_user.id, bots_message.message_id)
    if isinstance(result, Exception):
        result = restbot_db_helper.update_message_id_of_admin(message.from_user.id, bots_message.message_id)
    if isinstance(result, Exception):
        print(result)


@router.callback_query(F.data == "back_button_call", IsRestbotAdmin())
async def back_to_admin_panel(call: types.CallbackQuery, state: FSMContext):

    await restbot_bot.delete_message(chat_id=call.from_user.id,
                                     message_id=get_current_message_id(call.from_user.id))
    new_message = await restbot_bot.send_message(
        text=f'Выберите действие:',
        reply_markup=admin_keyboard,
        chat_id=call.from_user.id,
    )
    restbot_db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)
    await state.clear()
    await call.answer()


@router.callback_query(F.data == "sending_restaurant", IsRestbotAdmin())
async def start_sending(call: types.CallbackQuery, state: FSMContext):

    await restbot_bot.delete_message(chat_id=call.from_user.id,
                                     message_id=get_current_message_id(call.from_user.id))
    new_message = await restbot_bot.send_message(
        text="Введите текст сообщения для рассылки", chat_id=call.from_user.id,
        reply_markup=back_button_keyboard
    )
    restbot_db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)
    await state.set_state(Sending.GetMessage)
    await call.answer()


@router.message(Sending.GetMessage, IsRestbotAdmin())
async def get_message_for_sending(message: types.Message, state: FSMContext):
    text = message.text

    await restbot_bot.delete_message(chat_id=message.from_user.id,
                                     message_id=get_current_message_id(message.from_user.id))
    new_message = await restbot_bot.send_message(
        text=f"Ваше сообщение: \n{text}\n\nОтправить?", chat_id=message.from_user.id,
        reply_markup=send_message_keyboard
    )
    restbot_db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)
    await restbot_bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await state.update_data(text=text)
    await state.set_state(Sending.SendMessage)


@router.callback_query(Sending.SendMessage, F.data == "send_message_call", IsRestbotAdmin())
async def send_sending_message(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message = data.get('text')
    success = []
    failed = []
    for user in restbot_db_helper.select_all_users():
        try:
            await restbot_bot.send_message(user[0], message)
            success.append(user[0])
        except Exception as err:
            logging.error(err)
            failed.append(user[0])
    for admin in get_admins():
        try:
            await restbot_bot.send_message(admin, f"Выполнена рассылка\n\nПолучили сообщение: {success}\n\n"
                                                  f"Не получили сообщение: {failed}\n\nСообщение: {message}")
        except Exception as err:
            logging.error(err)
    await call.answer()
    await state.clear()


@router.callback_query(F.data == "load_orders_history", IsRestbotAdmin())
async def send_orders_history(call: types.callback_query):
    response = await download_file_to_restbot(get_restaurant_url() + f'/get_orders?restId={get_restaurant_id()}',
                                              'OrdersList.xlsx')
    if response.status_code == 200:
        if os.path.exists("OrdersList.xlsx"):
            file = FSInputFile("OrdersList.xlsx")
            await restbot_bot.send_document(chat_id=call.from_user.id, document=file)

            await restbot_bot.delete_message(chat_id=call.from_user.id,
                                     message_id=get_current_message_id(call.from_user.id))
            new_message = await restbot_bot.send_message(
                chat_id=call.from_user.id,
                text=f"Файл отправлен",
                reply_markup=back_button_keyboard
            )
            restbot_db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)

        else:
            await restbot_bot.delete_message(chat_id=call.from_user.id,
                                             message_id=get_current_message_id(call.from_user.id))
            new_message = await restbot_bot.send_message(
                chat_id=call.from_user.id,
                text=f"Ошибка получения файла {response.status_code}\nПопробуйте еще раз",
                reply_markup=back_button_keyboard
            )
            restbot_db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)
    else:
        await restbot_bot.delete_message(chat_id=call.from_user.id,
                                         message_id=get_current_message_id(call.from_user.id))
        new_message = await restbot_bot.send_message(
            chat_id=call.from_user.id,
            text=f"Ошибка получения файла {response.status_code}\nПопробуйте еще раз",
            reply_markup=back_button_keyboard
        )
        restbot_db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)


