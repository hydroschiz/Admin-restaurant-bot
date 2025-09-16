import os.path

from aiogram import types, exceptions, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from data.config import URL_DOWNLOAD_RESTAURANTS_LIST
from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import admin_panel_buttons, restaurants_list_buttons, \
    restaurants_list_error_buttons, back_button_keyboard, restaurants_list_columns
from loader import bot, get_current_message_id, db_helper
from states.delete_restaurant_state import DeleteRestaurant
from states.edit_restaurant_state import EditRestaurant
from utils.requests_to_db import download_file, delete_restaurant_from_db, edit_restaurant_in_db

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
    new_message = await bot.send_message(
        chat_id=call.from_user.id,
        text=f"Выберите действие:",
        reply_markup=admin_panel_buttons
    )
    db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)

    await state.clear()
    await call.answer()


@router.callback_query(F.data == "get_restaurants_list")
async def send_restaurants_list(call: types.CallbackQuery, state: FSMContext):
    response = await download_file(URL_DOWNLOAD_RESTAURANTS_LIST, 'data', 'RestaurantsList.xlsx')
    if response.status_code == 200:
        if os.path.exists("data/RestaurantsList.xlsx"):
            file = FSInputFile("data/RestaurantsList.xlsx")
            await bot.send_document(chat_id=call.from_user.id, document=file)

            await bot.delete_message(chat_id=call.from_user.id,
                                     message_id=get_current_message_id(call.from_user.id))
            new_message = await bot.send_message(
                chat_id=call.from_user.id,
                text=f"Файл отправлен",
                reply_markup=restaurants_list_buttons
            )
            db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)

        else:
            await bot.delete_message(chat_id=call.from_user.id,
                                     message_id=get_current_message_id(call.from_user.id))
            new_message = await bot.send_message(
                chat_id=call.from_user.id,
                text=f"Ошибка получения файла {response.status_code}\nПопробуйте еще раз",
                reply_markup=restaurants_list_error_buttons
            )
            db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)
    else:
        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=get_current_message_id(call.from_user.id))
        new_message = await bot.send_message(
            chat_id=call.from_user.id,
            text=f"Ошибка получения файла {response.status_code}\nПопробуйте еще раз",
            reply_markup=restaurants_list_error_buttons
        )
        db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)


@router.callback_query(F.data == "delete_restaurant", IsAdmin())
async def start_deleting_restaurant(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=get_current_message_id(call.from_user.id))
    new_message = await bot.send_message(
        chat_id=call.from_user.id,
        text=f"Введите id ресторана из списка",
        reply_markup=restaurants_list_buttons
    )
    db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)

    await state.set_state(DeleteRestaurant.InputID)


@router.message(DeleteRestaurant.InputID, IsAdmin())
async def delete_restaurant_by_id(message: types.Message, state: FSMContext):
    restaurant_id = message.text
    try:
        int(restaurant_id)
    except ValueError:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Ошибка: id должен быть числом\nВведите еще раз",
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

        return
    if int(restaurant_id) < 0:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Ошибка: id должен быть числом\nВведите еще раз",
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)
        return

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    response = await delete_restaurant_from_db(restaurant_id)

    try:
        if response.status_code == 200 and response.json().get('status') == 'success':
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=get_current_message_id(message.from_user.id))
            new_message = await bot.send_message(
                chat_id=message.from_user.id,
                text=f"Ресторан {restaurant_id} удалён из базы",
                reply_markup=back_button_keyboard
            )
            db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

            await state.clear()
            return
        elif response.json().get('status') == 'error':
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=get_current_message_id(message.from_user.id))
            new_message = await bot.send_message(
                chat_id=message.from_user.id,
                text=f"Ошибка удаления {response.json().get('message')}. Введите id ещё раз, чтобы повторить",
                reply_markup=back_button_keyboard
            )
            db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

            return
        else:
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=get_current_message_id(message.from_user.id))
            new_message = await bot.send_message(
                chat_id=message.from_user.id,
                text=f"Ошибка удаления {response.status_code}. Введите id ещё раз, чтобы повторить",
                reply_markup=back_button_keyboard
            )
            db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)
            return
    except Exception as e:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Ошибка удаления {e}. Введите id ещё раз, чтобы повторить",
            message_id=get_current_message_id(message.from_user.id),
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

        return


@router.callback_query(F.data == "edit_restaurants_list", IsAdmin())
async def start_editing_restaurant(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=get_current_message_id(call.from_user.id))
    new_message = await bot.send_message(
        chat_id=call.from_user.id,
        text=f"Введите id ресторана из списка",
        reply_markup=restaurants_list_buttons
    )
    db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)
    await state.set_state(EditRestaurant.InputID)


@router.message(EditRestaurant.InputID, IsAdmin())
async def input_id_to_edit_restaurant(message: types.Message, state: FSMContext):
    restaurant_id = message.text
    try:
        int(restaurant_id)
    except ValueError:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Ошибка: id должен быть числом\nВведите еще раз",
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)
        return
    if int(restaurant_id) < 0:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Ошибка: id должен быть числом\nВведите еще раз",
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)
        return

    await bot.delete_message(chat_id=message.from_user.id,
                             message_id=get_current_message_id(message.from_user.id))
    new_message = await bot.send_message(
        chat_id=message.from_user.id,
        text=f"Выберите колонку для редактирования",
        reply_markup=restaurants_list_columns
    )
    db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)
    await state.set_state(EditRestaurant.SelectColumn)
    await state.update_data(restaurant_id=restaurant_id)


@router.callback_query(F.data.in_(["edit_restaurant_name", "edit_bot_token", "edit_api_foodcard_token",
                                   "edit_admin_id_1", "edit_admin_id_2", "edit_admin_id_3"]), IsAdmin())
async def select_column_to_edit(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(column=call.data)
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=get_current_message_id(call.from_user.id))
    new_message = await bot.send_message(
        chat_id=call.from_user.id,
        text=f"Введите значение",
        reply_markup=back_button_keyboard
    )
    db_helper.update_message_id_of_admin(call.from_user.id, new_message.message_id)
    await state.set_state(EditRestaurant.InputValue)


@router.message(EditRestaurant.InputValue, IsAdmin())
async def input_value_to_edit(message: types.Message, state: FSMContext):
    value = message.text
    data = await state.get_data()
    column = data.get('column')
    restaurant_id = data.get('restaurant_id')

    response = await edit_restaurant_in_db(restaurant_id, column, value)
    if response.status_code == 200:
        print(response.json())

        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Данные изменены",
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)
    else:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=get_current_message_id(message.from_user.id))
        new_message = await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Ошибка изменения данных {response.status_code}\nПопробуйте ещё раз",
            reply_markup=back_button_keyboard
        )
        db_helper.update_message_id_of_admin(message.from_user.id, new_message.message_id)

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
