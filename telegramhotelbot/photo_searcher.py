import json

import requests
from decouple import config

TOKEN_API = config('TOKEN_API')


def photo_url(count: int, hotel_id: int) -> str or None:
    """
    Ищет и выводит url фотографий отеля в API.

    :param count: int Количество фотографий
    :param hotel_id: int ID отеля
    :return: list URL фотографий
    """

    photo_url_f = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    photo_querystring = {"id": f"{hotel_id}"}
    photo_headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': TOKEN_API
    }
    photo_response = requests.request("GET", photo_url_f, headers=photo_headers, params=photo_querystring)
    data = json.loads(photo_response.text)
    try:
        photo = [data["hotelImages"][i]["baseUrl"].replace("{size}", "b") for i in range(count)]
    except KeyError:
        return None
    return photo
