import datetime
import json
import os.path
import pathlib
import re
import subprocess

from aiogram import Router, F, types, exceptions
from aiogram.fsm.context import FSMContext

from data.config import DEPLOY_PATH, BOT_PATH
from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import admin_panel_buttons, back_button_keyboard, send_data_to_db_keyboard
from loader import bot, get_current_message_id, db_helper
from states.add_restaurant_state import AddRestaurant
from utils.requests_to_db import send_data_to_db

router = Router()


@router.callback_query(F.data == "back_to_admin_panel", IsAdmin())
async def get_back_to_admin_panel(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_message = data.get("message")
    if bot_message:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=bot_message.message_id)
        except exceptions.TelegramBadRequest:
            pass
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=get_current_message_id(call.from_user.id))
    new_message = await bot.send_message(chat_id=call.from_user.id,
                           text=f"Выберите действие:",
                           reply_markup=admin_panel_buttons)
    db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)

    await state.clear()
    await call.answer()


@router.callback_query(F.data == "add_restaurant", IsAdmin())
async def start_adding_restaurant(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=get_current_message_id(call.from_user.id))
    new_message = await bot.send_message(text="Введите название ресторана", chat_id=call.from_user.id,
                                         reply_markup=back_button_keyboard)
    db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)
    await state.set_state(AddRestaurant.SetName)
    await call.answer()


@router.message(AddRestaurant.SetName, IsAdmin())
async def set_restaurant_name(message: types.Message, state: FSMContext):
    restaurant_name = message.text

    await state.update_data(restaurant_name=restaurant_name)

    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=get_current_message_id(message.from_user.id))

    new_message = await bot.send_message(text=f"Введите API токен Telegram бота", chat_id=message.from_user.id,
                                         reply_markup=back_button_keyboard)
    db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await state.set_state(AddRestaurant.SetBotToken)


@router.message(AddRestaurant.SetBotToken, IsAdmin())
async def set_bot_token(message: types.Message, state: FSMContext):
    bot_token = message.text

    if not re.match(r'^\d{8,10}:[A-Za-z0-9_-]{35}$', bot_token):
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            text=f"Неверный токен. \nВведите API токен Telegram бота",
            chat_id=message.from_user.id,
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

        return
    await state.update_data(bot_token=bot_token)

    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=get_current_message_id(message.from_user.id))
    new_message = await bot.send_message(text=f"Введите Telegram ID администратора 1", chat_id=message.from_user.id,
                                reply_markup=back_button_keyboard)
    db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await state.set_state(AddRestaurant.SetAdminID1)


@router.message(AddRestaurant.SetAdminID1, IsAdmin())
async def set_admin_id_1(message: types.Message, state: FSMContext):
    admin_id = message.text

    try:
        int(admin_id)
    except ValueError:

        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = bot.send_message(
            text=f"Неверный ID. \nВведите Telegram ID администратора",
            chat_id=message.from_user.id,
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        return
    await state.update_data(admin_id_1=admin_id)

    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=get_current_message_id(message.from_user.id))
    new_message = await bot.send_message(
        text=f"Введите Telegram ID администратора 2", chat_id=message.from_user.id,
        reply_markup=back_button_keyboard
    )
    db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await state.set_state(AddRestaurant.SetAdminID2)


@router.message(AddRestaurant.SetAdminID2, IsAdmin())
async def set_admin_id_2(message: types.Message, state: FSMContext):
    admin_id = message.text

    try:
        int(admin_id)
    except ValueError:

        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            text=f"Неверный ID. \nВведите Telegram ID администратора",
            chat_id=message.from_user.id,
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        return
    await state.update_data(admin_id_2=admin_id)

    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=get_current_message_id(message.from_user.id))
    new_message = await bot.send_message(
        text=f"Введите Telegram ID администратора 3", chat_id=message.from_user.id,
        reply_markup=back_button_keyboard
    )
    db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await state.set_state(AddRestaurant.SetAdminID3)


@router.message(AddRestaurant.SetAdminID3, IsAdmin())
async def set_admin_id_3(message: types.Message, state: FSMContext):
    admin_id = message.text

    try:
        int(admin_id)
    except ValueError:

        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            text=f"Неверный ID. \nВведите Telegram ID администратора",
            chat_id=message.from_user.id,
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        return
    await state.update_data(admin_id_3=admin_id)

    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=get_current_message_id(message.from_user.id))
    new_message = await bot.send_message(
        text=f"Введите Auth токен FoodCard", chat_id=message.from_user.id,
        reply_markup=back_button_keyboard
    )
    db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await state.set_state(AddRestaurant.SetAuthToken)


@router.message(AddRestaurant.SetAuthToken, IsAdmin())
async def set_auth_token(message: types.Message, state: FSMContext):
    auth_token = message.text

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await state.update_data(auth_token=auth_token)
    await state.set_state(AddRestaurant.Deploy)
    await send_data(message, state)


async def send_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    restaurant_name = data.get('restaurant_name')
    bot_token = data.get('bot_token')
    admin_id_1 = data.get('admin_id_1')
    admin_id_2 = data.get('admin_id_2')
    admin_id_3 = data.get('admin_id_3')
    auth_token = data.get('auth_token')

    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=get_current_message_id(message.from_user.id))
    new_message = await bot.send_message(
        text=f"Название ресторана: {restaurant_name},\n"
             f"Токен бота: {bot_token},\n"
             f"ID администратора 1: {admin_id_1}, \n"
             f"ID администратора 2: {admin_id_2}, \n"
             f"ID администратора 3: {admin_id_3}, \n"
             f"Auth токен: {auth_token}\n"
             f"", chat_id=message.from_user.id,
        reply_markup=send_data_to_db_keyboard
    )
    db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

    @router.callback_query(F.data == "send_data_callback", IsAdmin())
    async def send_data_to_db_call(call: types.CallbackQuery):
        try:
            response = await send_data_to_db(restaurant_name, bot_token, admin_id_1, admin_id_2, admin_id_3, auth_token)
        except Exception as e:

            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=get_current_message_id(message.from_user.id))
            new_message = await bot.send_message(
                text=f"Ошибка отправки {e}. Попробуйте еще раз.\n"
                     f"Название ресторана: {restaurant_name},\n"
                     f"Токен бота: {bot_token},\n"
                     f"ID администратора 1: {admin_id_1}, \n"
                     f"ID администратора 2: {admin_id_2}, \n"
                     f"ID администратора 3: {admin_id_3}, \n"
                     f"Auth токен: {auth_token}\n"
                     f"", chat_id=message.from_user.id,
                reply_markup=send_data_to_db_keyboard
            )
            db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

            await call.answer()
            return
        if response.status_code == 200:
            link = response.json().get('link')
            restaurant_id = response.json().get('restaurant_id')

            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=get_current_message_id(message.from_user.id))

            await message.answer(f'Ссылка на сайт ресторана: {link}\nСохраните ссылку')
            deploy_result = await deploy_restaurant_to_server(restaurant_name, link, restaurant_id, bot_token,
                                                             admin_id_1, admin_id_2, admin_id_3, auth_token)
            if isinstance(deploy_result, Exception):
                await message.answer(f'Ошибка развертывания на сервере {deploy_result}')
            else:
                await message.answer(f'Результат развертывания на сервере: \n\n{deploy_result}')

            new_message = await bot.send_message(
                text=f"Данные отправлены", chat_id=message.from_user.id,
                reply_markup=back_button_keyboard
            )
            db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

            await state.clear()
            await call.answer()
            return

        else:

            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=get_current_message_id(message.from_user.id))
            new_message = await bot.send_message(
                text=f"Ошибка отправки {response.status_code}. Попробуйте еще раз.\n"
                     f"Название ресторана: {restaurant_name},\n"
                     f"Токен бота: {bot_token},\n"
                     f"ID администратора 1: {admin_id_1}, \n"
                     f"ID администратора 2: {admin_id_2}, \n"
                     f"ID администратора 3: {admin_id_3}, \n"
                     f"Auth токен: {auth_token}\n"
                     f"", chat_id=message.from_user.id,
                reply_markup=send_data_to_db_keyboard
            )
            db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)
            await call.answer()
            return


async def deploy_restaurant_to_server(restaurant_name, link, restaurant_id, bot_token, admin_id_1, admin_id_2, admin_id_3, auth_token):
    date = datetime.datetime.now().strftime("%Y%m%d")
    deploy_path = DEPLOY_PATH.format(user_id=admin_id_1, date=date)
    bot_path = BOT_PATH

    config = {
      "RESTAURANT_NAME": restaurant_name,
      "RESTAURANT_URL": link,
      "RESTAURANT_ID": restaurant_id,
      "BOT_TOKEN": bot_token,
      "ADMIN_ID_1": admin_id_1,
      "ADMIN_ID_2": admin_id_2,
      "ADMIN_ID_3": admin_id_3,
      "API_FOODCARD_TOKEN": auth_token
    }

    with open('rest_bot/restbot_data.json', "w", encoding='utf-8') as outfile:
        json.dump(config, outfile)

    system_service = f"""
[Unit]
Description=Example - Telegram Bot

After=syslog.target 
After=network.target


[Service] 
Type=simple 
WorkingDirectory={deploy_path}
ExecStart={deploy_path}/venv/bin/python3 {deploy_path}/restbot_bot.py 
RestartSec=30
Restart=always

[Install] 
WantedBy=multi-user.target
    """

    # Подготовка команд для деплоя и настройки службы systemd
    commands = f"""
        if [ -d {deploy_path} ]; then
            rm -rf {deploy_path}
        fi


        mkdir -p {deploy_path}
        
        cd {deploy_path}
        python3 -m venv venv

        cat {bot_path}/rest_bot/restbot_data.json > {deploy_path}/restbot_data.json
        cat {bot_path}/rest_bot/restbot_bot.py > {deploy_path}/restbot_bot.py
        cat {bot_path}/rest_bot/restbot_config.py > {deploy_path}/restbot_config.py
        cat {bot_path}/rest_bot/restbot_filters.py > {deploy_path}/restbot_filters.py
        cat {bot_path}/rest_bot/restbot_handlers.py > {deploy_path}/restbot_handlers.py
        cat {bot_path}/rest_bot/restbot_keyboards.py > {deploy_path}/restbot_keyboards.py
        cat {bot_path}/rest_bot/restbot_sqlite.py > {deploy_path}/restbot_sqlite.py
        cat {bot_path}/requirements.txt > {deploy_path}/requirements.txt
        
        {deploy_path}/venv/bin/python3 -m pip install -r requirements.txt

        echo '{system_service}' > /lib/systemd/system/bot_{admin_id_1}_{date}.service
        systemctl daemon-reload
        systemctl enable bot_{admin_id_1}_{date}.service
        systemctl start bot_{admin_id_1}_{date} 
        systemctl status bot_{admin_id_1}_{date}.service > {deploy_path}/status.txt
        
        """

    try:
        subprocess.run(commands, shell=True, check=True)
        status = None
        if os.path.exists(f'{deploy_path}/status.txt'):
            with open(f'{deploy_path}/status.txt') as status_file:
                status = status_file.read()
        return status
    except subprocess.CalledProcessError as e:
        print('Ошибка при развертывании', e)
        return e
