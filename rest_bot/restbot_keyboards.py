from urllib.parse import urlparse

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from restbot_config import get_restaurant_url


def parse_domain(url):
    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}/"
    return domain


user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Перейти в меню", web_app=WebAppInfo(url=(get_restaurant_url() + "menu")))
        ],
        [
            InlineKeyboardButton(text="Корзина", web_app=WebAppInfo(url=(get_restaurant_url() + "basket")))
        ],
    ]
)


admin_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Рассылка по ресторану", callback_data="sending_restaurant")
        ],
        [
            InlineKeyboardButton(text="Выгрузить историю заказов", callback_data="load_orders_history")
        ],
        [
            InlineKeyboardButton(text="История заказов", web_app=WebAppInfo(url=(parse_domain(get_restaurant_url()) + "order_history")))
        ],
        [
            InlineKeyboardButton(text="Редактировать меню", web_app=WebAppInfo(url=(get_restaurant_url() + "edit_menu")))
        ],
    ]
)


back_button_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back_button_call")
        ],
    ]
)

send_message_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отправить", callback_data="send_message_call")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_button_call")
        ],
    ]
)