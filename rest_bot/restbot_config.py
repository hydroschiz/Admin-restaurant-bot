import asyncio
import json

import requests


def get_bot_token():
    with open("restbot_data.json", "r") as jsonFile:
        restbot_data = json.load(jsonFile)
        bot_token = restbot_data["BOT_TOKEN"]
    return bot_token


def get_api_foodcard_token():
    with open("restbot_data.json", "r") as jsonFile:
        restbot_data = json.load(jsonFile)
        api_foodcard_token = restbot_data["API_FOODCARD_TOKEN"]
    return api_foodcard_token


def get_restaurant_name():
    with open("restbot_data.json", "r") as jsonFile:
        restbot_data = json.load(jsonFile)
        restaurant_name = restbot_data["RESTAURANT_NAME"]
    return restaurant_name


def get_restaurant_id():
    with open("restbot_data.json", "r") as jsonFile:
        restbot_data = json.load(jsonFile)
        restaurant_id = restbot_data["RESTAURANT_ID"]
    return restaurant_id


def get_restaurant_url():
    with open("restbot_data.json", "r") as jsonFile:
        restbot_data = json.load(jsonFile)
        restaurant_url = restbot_data["RESTAURANT_URL"]
    return restaurant_url


def get_admins():
    with open("restbot_data.json", "r") as jsonFile:
        restbot_data = json.load(jsonFile)
        admin_id_1 = restbot_data["ADMIN_ID_1"]
        admin_id_2 = restbot_data["ADMIN_ID_2"]
        admin_id_3 = restbot_data["ADMIN_ID_3"]
    return [admin_id_1, admin_id_2, admin_id_3]


async def auto_update_restbot_data(file_path='restbot_data.json', interval=600):
    while True:
        try:
            await asyncio.sleep(interval)
            headers = {
                'Content-Type': 'application/json',
            }

            data = {
                'id': get_restaurant_id()
            }

            json_data = json.dumps(data)

            response = requests.post(get_restaurant_url() + 'get_rest_info', headers=headers, data=json_data)
            response_json = response.json()

            with open(file_path, 'r', encoding='utf-8') as file:
                restbot_data = json.load(file)

            # Получение данных из response
            if response_json.get('success'):
                restaurant_info = response_json.get('restaurant', {})

                # Обновление соответствующих полей
                restbot_data['RESTAURANT_NAME'] = restaurant_info.get('restaurant_name', restbot_data['RESTAURANT_NAME'])
                restbot_data['RESTAURANT_URL'] = restaurant_info.get('restaurant_url', restbot_data['RESTAURANT_URL'])
                restbot_data['BOT_TOKEN'] = restaurant_info.get('bot_token', restbot_data['BOT_TOKEN'])
                restbot_data['ADMIN_ID_1'] = restaurant_info.get('admin_id_1', restbot_data['ADMIN_ID_1'])
                restbot_data['ADMIN_ID_2'] = restaurant_info.get('admin_id_2', restbot_data['ADMIN_ID_2'])
                restbot_data['ADMIN_ID_3'] = restaurant_info.get('admin_id_3', restbot_data['ADMIN_ID_3'])
                restbot_data['API_FOODCARD_TOKEN'] = restaurant_info.get('api_foodcard_token',
                                                                         restbot_data['API_FOODCARD_TOKEN'])

                # Запись обновленных данных обратно в JSON файл
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(restbot_data, file)
        except Exception as e:
            print(e)
