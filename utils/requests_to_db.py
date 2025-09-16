import os

import requests
import json

from data.config import URL_ADD_TO_DB, URL_DELETE_FROM_DB, URL_EDIT_IN_DB

url_add = URL_ADD_TO_DB
url_delete = URL_DELETE_FROM_DB
url_edit = URL_EDIT_IN_DB


async def send_data_to_db(restaurant_name, bot_token, admin_id_1, admin_id_2, admin_id_3, auth_token):
    data = {
        'restaurant_name': restaurant_name,
        'bot_token': bot_token,
        'admin_id_1': admin_id_1,
        'admin_id_2': admin_id_2,
        'admin_id_3': admin_id_3,
        'auth_token': auth_token,
    }

    json_data = json.dumps(data)

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json'
    }

    # Отправка POST-запроса с JSON-данными
    response = requests.post(url_add, headers=headers, data=json_data)

    return response


async def delete_restaurant_from_db(restaurant_id):
    data = {
        'id': restaurant_id,
    }

    json_data = json.dumps(data)

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json'
    }

    # Отправка POST-запроса с JSON-данными
    response = requests.post(url_delete, headers=headers, data=json_data)

    return response


async def edit_restaurant_in_db(restaurant_id, column, value):
    data = {
        'id': restaurant_id,
        'column': column,
        'value': value
    }

    json_data = json.dumps(data)

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json'
    }

    # Отправка POST-запроса с JSON-данными
    response = requests.post(url_edit, headers=headers, data=json_data)

    return response


async def download_file(url, directory, file_name):
    save_path = os.path.join(directory, file_name)

    response = requests.get(url, verify=False)

    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)

    return response

