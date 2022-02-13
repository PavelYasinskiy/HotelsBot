from telebot import types
import telebot
import requests
import json
import re
bot = telebot.TeleBot('5097527148:AAE5i3807lIHTBVl-WXFHn0_sYEe6THdl_0')
def city_id_searcher(city):
    city_name = city
    print(city_name)
    if city_name != None:
        city_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        city_querystring = {"query": f"{city_name}", "locale": "ru_RU"}
        city_headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "2348478bc2msh746d87ae988083bp1b5dc8jsn48d3b426aa8f"
            }
        city_response = requests.request("GET", city_url, headers=city_headers, params=city_querystring)
        if city_response.status_code != 200:
            return None
        city_id = json.loads(city_response.text)
        founded_cities = [i for i in range(len(city_id["suggestions"][0]["entities"]))
                          if city_name.split(" ") == city_id["suggestions"][0]["entities"][i]["name"].split(' ')
                          or city_name.split("-") == city_id["suggestions"][0]["entities"][i]["name"].split('-')
                          or city_name.split("-") == city_id["suggestions"][0]["entities"][i]["name"].split(' ')
                          or city_name.split(" ") == city_id["suggestions"][0]["entities"][i]["name"].split('-')
                          ]

        print(founded_cities)
        if len(founded_cities) == 0:
            return None
        else:
            city = city_id["suggestions"][0]["entities"][founded_cities[0]]["destinationId"]
            city_name = city_id["suggestions"][0]["entities"][founded_cities[0]]["name"]
            return [city, city_name]
    else:
        return None