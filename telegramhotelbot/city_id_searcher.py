import json

import requests
from decouple import config

TOKEN_API = config('TOKEN_API')


def city_id_searcher(city: str) -> list or None:
    """
    Обращается к API и ищет id города, введенного пользователем.
    Возвращает название города и id.
    :param city: str Название города
    :return: list Возвращает название города и id.
    """
    city_name = city
    if city_name is not None:
        city_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        city_querystring = {"query": f"{city_name}", "locale": "ru_RU"}
        city_headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': TOKEN_API
        }
        try:
            city_response = requests.request("GET",
                                             city_url,
                                             headers=city_headers,
                                             params=city_querystring,
                                             timeout=(3, 8))
        except requests.exceptions.Timeout:
            return 'Timeout'
        if city_response.status_code != 200:
            return None
        city_id = json.loads(city_response.text)
        founded_cities = [i for i in range(len(city_id["suggestions"][0]["entities"]))
                          if city_name.split(" ") == city_id["suggestions"][0]["entities"][i]["name"].split(' ')
                          or city_name.split("-") == city_id["suggestions"][0]["entities"][i]["name"].split('-')
                          or city_name.split("-") == city_id["suggestions"][0]["entities"][i]["name"].split(' ')
                          or city_name.split(" ") == city_id["suggestions"][0]["entities"][i]["name"].split('-')
                          ]
        if len(founded_cities) == 0:
            return None
        else:
            city = city_id["suggestions"][0]["entities"][founded_cities[0]]["destinationId"]
            city_name = city_id["suggestions"][0]["entities"][founded_cities[0]]["name"]
            return [city, city_name]
    else:
        return None
