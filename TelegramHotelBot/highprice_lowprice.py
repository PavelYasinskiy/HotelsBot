import json
import requests
import datetime
from TelegramHotelBot import history, photo_searcher
from decouple import config

TOKEN_API = config('TOKEN_API')

def hotelsFinder(info: list) ->list:
    """
    Ищет отели по информации пользователя.
    Отбирает самые дешевые отели расположенные или самые дорогие, в зависимости от команды пользователя.
    Преващает информацию из API в читаемый для пользователя список.

    :param info: list Информация пользователя
    :return: Список информации по отелям для пользователя.
    """
    user_info = info
    city = user_info[2]
    hotels_output = user_info[10]
    checkIn = user_info[6]
    checkOut = user_info[7]
    photo_count = int(user_info[11])
    days = (datetime.datetime.strptime(user_info[7], "%Y-%m-%d").date()-
            datetime.datetime.strptime(user_info[6], "%Y-%m-%d").date()).days
    if user_info[1] == "lowprice":
        price_filter = "PRICE"
    else:
        price_filter ="HIGHT_PRICE_FIRST"



    hotels_url = "https://hotels4.p.rapidapi.com/properties/list"
    hotels_querystring = {"destinationId": f"{city}", "pageNumber": "1",
                          "pageSize": f"{hotels_output}", "checkIn": f"{checkIn}",
                   "checkOut": f"{checkOut}", "adults1": "1",
                   "sortOrder": f"{price_filter}", "locale": "ru_RU", "currency": "RUB"}
    print(hotels_querystring)
    hotels_headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': TOKEN_API
        }
    hotels_response = requests.request("GET", url=hotels_url, headers=hotels_headers, params=hotels_querystring)
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
        hotel_names.append(data_short[i]['name'])
        try:
            streetAddress = data_short[i]['address']['streetAddress']
        except KeyError:
            streetAddress = "Нет информации об адресе. Уточняйте на сайте отеля"
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
            photo_url = photo_searcher.photo_url(count=photo_count, id=hotel_id)
            result.append((photo_url, f"Отель {data_short[i]['name']}\n"
                  f"Адрес: {streetAddress},{locality},"
                  f"{data_short[i]['address']['countryName']}\n"
                  f"Удаленность от центра: {data_short[i]['landmarks'][0]['distance']}\n"
                  f"Цена за {days} {days_name}: {price}\n"
                  f"Цена за ночь {cur_price} RUB\n\n\n"
                  f"Ссылка на сайт: https://ru.hotels.com/ho{hotel_id}"))
    history.add_history(info=user_info, names=hotel_names)
    return result


