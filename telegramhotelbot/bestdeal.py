import json
import datetime

import requests
from decouple import config

from telegramhotelbot import history, photo_searcher


TOKEN_API = config('TOKEN_API')


def hotels_finder(info: list) -> list or None:
    """
    Ищет отели и отбирает их по цене, введенной пользователем.
    Отбирает самые дешевые отели расположенные ближе всего к
    центру города. Преващает информацию из API в читаемый для пользователя список.

    :param info: list Информация пользователя
    :return: Список информации по отелям для пользователя.
    """
    user_info = info
    city = user_info[2]
    hotels_output = user_info[10]
    check_in = user_info[6]
    check_out = user_info[7]
    price_max = user_info[5]
    price_min = user_info[4]
    distance_min = int(user_info[8])
    distance_max = int(user_info[9])
    photo_count = int(user_info[11])
    days = (datetime.datetime.strptime(user_info[7], "%Y-%m-%d").date() -
            datetime.datetime.strptime(user_info[6], "%Y-%m-%d").date()).days

    hotels_url = "https://hotels4.p.rapidapi.com/properties/list"
    hotels_querystring = {"destinationId": f"{city}", "pageNumber": "1",
                          "pageSize": f"{hotels_output}",
                          "checkIn": f"{check_in}",
                          "checkOut": f"{check_out}",
                          "adults1": "1",
                          "priceMin": f'{price_min}',
                          "priceMax": f'{price_max}',
                          "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}
    hotels_headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': TOKEN_API
    }
    try:
        hotels_response = requests.request("GET",
                                           url=hotels_url,
                                           headers=hotels_headers,
                                           params=hotels_querystring,
                                           timeout=(3, 8))
    except requests.exceptions.Timeout:
        return ["К сожалению сервер c отелями сейчас недоступен,\n"
                "Попробуйте еще раз или зайдите позднее"]
    hotels_response.encoding = "utf-8"
    data = json.loads(hotels_response.text)
    if len(data['data']['body']['searchResults']["results"]) == 0:
        return ["Нет отелей, подходящих под ваш запрос.\n"
                "Попробуйте изменить параметры поиска."]
    data_short = data['data']['body']['searchResults']["results"]
    result = []
    hotel_names = []
    if days % 10 == 1 and days != 11:
        days_name = "день"
    elif days % 10 in [2, 3, 4] and days not in [12, 13, 14]:
        days_name = "дня"
    else:
        days_name = 'дней'
    for i in range(int(hotels_output)):
        if distance_max >\
                float(data_short[i]['landmarks'][0]['distance'].split(' ')[0].replace(",", ".")) \
                > distance_min:
            hotel_names.append(data_short[i]['name'])
            try:
                street_address = data_short[i]['address']['streetAddress']
            except KeyError:
                street_address = "Нет информации об адресе. Уточняйте на сайте отеля"
            try:
                locality = data_short[i]['address']['locality']
            except KeyError:
                locality = " "
            try:
                price = data_short[i]['ratePlan']['price']['current']
                cur_price = round(data_short[i]['ratePlan']['price']['exactCurrent'] / days, 0)
            except KeyError:
                price = "Нет информации. Уточняйте на сайте отеля"
                cur_price = 'Нет информации. Уточняйте на сайте отеля'
            finally:
                hotel_id = data_short[i]['id']
                photo_url = photo_searcher.photo_url(count=photo_count, hotel_id=hotel_id)
                result.append((photo_url, f"Отель {data_short[i]['name']}\n"
                                          f"Адрес: {street_address},{locality},"
                                          f"{data_short[i]['address']['countryName']}\n"
                                          f"Удаленность от центра: {data_short[i]['landmarks'][0]['distance']}\n"
                                          f"Цена за {days} {days_name}: {price}\n"
                                          f"Цена за ночь {cur_price} RUB\n\n\n"
                                          f"Ссылка на сайт: https://ru.hotels.com/ho{hotel_id}"))
    if len(hotel_names) == 0:
        return ["Нет отелей, подходящих под ваш запрос.\n"
                "Попробуйте изменить параметры поиска."]
    history.add_history(info=user_info, names=hotel_names)
    return result
