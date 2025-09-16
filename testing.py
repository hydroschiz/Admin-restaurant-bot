import json

import requests

from rest_bot.restbot_config import get_restaurant_id, get_restaurant_url


async def auto_update_restbot_data(request, file_path='restbot_data.json'):
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
