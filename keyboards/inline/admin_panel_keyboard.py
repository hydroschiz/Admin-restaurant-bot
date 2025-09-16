from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import URL_INSTRUCTION

admin_panel_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить заведение", callback_data="add_restaurant")
        ],
        [
            InlineKeyboardButton(text="Список заведений", callback_data="get_restaurants_list")
        ],
        [
            InlineKeyboardButton(text="Инструкция", url=URL_INSTRUCTION)
        ],
    ]
)

back_button_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)

send_data_to_db_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отправить", callback_data="send_data_callback")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)

restaurants_list_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Редактировать", callback_data="edit_restaurants_list")
        ],
        [
            InlineKeyboardButton(text="Удалить ресторан", callback_data="delete_restaurant")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ],
    ]
)

restaurants_list_error_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Ещё раз", callback_data="get_restaurants_list")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ],
    ]
)

restaurants_list_columns = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Название ресторана", callback_data="edit_restaurant_name")
        ],
        [
            InlineKeyboardButton(text="Токен Telegram", callback_data="edit_bot_token")
        ],
        [
            InlineKeyboardButton(text="Токен API Foodcard", callback_data="edit_api_foodcard_token")
        ],
        [
            InlineKeyboardButton(text="ID администратора 1", callback_data="edit_admin_id_1")
        ],
        [
            InlineKeyboardButton(text="ID администратора 2", callback_data="edit_admin_id_2")
        ],
        [
            InlineKeyboardButton(text="ID администратора 3", callback_data="edit_admin_id_3")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ],
    ]
)