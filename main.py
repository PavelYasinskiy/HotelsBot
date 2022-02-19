import re
import datetime
import telebot
from loguru import logger
from telebot import types
from TelegramHotelBot import cityID_searcher, highprice_lowprice, bestdeal, history
from dbase import Data_Base
from decouple import config
import time
TOKEN_BOT = config('TOKEN_BOT')


from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

bot = telebot.TeleBot(TOKEN_BOT)

logger.add("logging.log", format='{time} {level} {message}', level="INFO", rotation="10 MB", compression="zip")

@logger.catch
@bot.message_handler(commands=['start'])
def start(message: types.Message):
    """
     Функция активации и преветствия после нажатия кнопки 'Start' в телеграм боте.
     Полсе приветствия переходит в функцию "help_message"

    :param message: принимает на вход сообщение от пользователя
    """

    logger.info(f'User {message.chat.id} used command "/start"')
    bot.send_message(chat_id=message.from_user.id, text=f"Привет,{message.from_user.first_name},"
                                                        f" я ищу отели по запросам!\n"
                                                        f"Вот что я могу")
    help_message(message)

@logger.catch
@bot.message_handler(commands=['help'])
def help_message(message: types.Message):
    """
    Функция отправляет пользователю информацию о существующих командах.
    Активируется при отправке пользователем сообщения '/help' либо при первом запуске из функции 'start'.

    :param message: принимает на вход сообщение от пользователя
    """

    logger.info(f'User {message.chat.id} used command "/help"')
    bot.send_message(message.from_user.id, "/help — помощь по командам бота\n"
                                           "/lowprice — самые дешёвые отели в городе\n"
                                           "/highprice — самые дорогие отели в городе\n"
                                           "/bestdeal — отели, наиболее подходящие по цене и расположению от центра\n"
                                           "/history — вывод истории поиска отелей\n")

@bot.message_handler(commands=['lowprice','highprice','bestdeal'])
def get_city(message: types.Message):
    """
    Функция, после определения команды, переданной пользователем, создает базу данных
    для пользователя и заполняет в ней первичную информацию (id, введенную команду поиска отеля).
    Отправляет сообщение пользователю о том, что ему необходимо ввести город и переходит в функцию поиска города.

    :param message: принимает на вход сообщение от пользователя с командой поиска ('lowprice','highprice','bestdeal')
    """

    logger.info(f'User {message.chat.id} used command {message.text}')

    Data_Base.create_info(message.chat.id)
    logger.info(f'User {message.chat.id} create a DataBase')
    Data_Base.add_info(column="command", value=message.text[1:], user_id=message.chat.id)
    Data_Base.add_info(column="checkIn_date", value=None, user_id=message.chat.id)
    Data_Base.add_info(column="checkOut_date", value=None, user_id=message.chat.id)
    Data_Base.add_info(column="price_min", value=None, user_id=message.chat.id)
    Data_Base.add_info(column="price_max", value=None, user_id=message.chat.id)
    Data_Base.add_info(column="distance_min", value=None, user_id=message.chat.id)
    Data_Base.add_info(column="distance_max", value=None, user_id=message.chat.id)
    logger.info(f'User {message.chat.id} create a DataBase')
    msg = bot.send_message(message.from_user.id, "Введите город:")
    bot.register_next_step_handler(msg, find_city_id)

@logger.catch
def find_city_id(message: types.Message):
    """
    Принимает на вход город, в котором будет производится поиск, обрабатывает запрос на ошибки ввода
    и ищет id города. Записывает информацию в базу данных. Если изначальный поиск был по команде 'bestdeal',
    переходит в функцию ввода минимальной и максимальной стоимости. В других случаях переходит в функцию
    приема даты заезда и выезда.

    :param message: На вход принимает название города отправленное пользователем
    :return:
    """
    city = message.text.title()
    logger.info(f'User {message.chat.id} enter city {city}')

    try:
        city_name = re.match(r'(\b(\D+)\b \b(\D+)\b)|(\b\D+\b)', city).group(0)
        if city_name.split(" ") != city.split(' ') and city_name.split("-") != city.split('-'):
            raise AttributeError
        elif city_name == None:
            raise AttributeError
    except AttributeError:
        msg = bot.send_message(message.from_user.id, "Ошибка. Введите корректное название города:")
        logger.info(f'User {message.chat.id} enter a wrong city')
        bot.register_next_step_handler(msg, find_city_id)
    else:
        city = cityID_searcher.city_id_searcher(city_name)
        if city in [None, 'None']:
            msg = bot.send_message(message.from_user.id, "Ошибка. Введите корректное название города:")
            logger.info(f'User {message.chat.id} enter a wrong city name.')
            bot.register_next_step_handler(msg, find_city_id)
        else:
            city_id = city[0]
            city_name = city[1]
            Data_Base.add_info(column="city_ID", value=int(city_id), user_id=message.chat.id)
            Data_Base.add_info(column="city_name", value=city_name, user_id=message.chat.id)
            bot.send_message(message.from_user.id, f"Ваш город: {city_name}")
            logger.info(f'User {message.chat.id} add city to DataBase')
            if Data_Base.show_info(message.chat.id)[1] == "bestdeal":
                msg = bot.send_message(message.from_user.id, f"Введите минимальную и "
                                                             f"максимальную стоимость в рублях через пробел")
                bot.register_next_step_handler(msg, input_prices)
            else:
                bot.send_message(message.from_user.id, f'Введите дату заезда')
                get_date(message)



@logger.catch
def input_prices(message: types.Message):
    """
    Принимает на вход максимальную и минимальную цену. Обрабатывает её на ошибки и записывает в базу данных.
    Переходит в функцию ввода расстояния от центра города.

    :param message:  Принимает на вход максимальную и минимальную цену.
    :return:
    """
    price_input = message.text
    logger.info(f'User {message.chat.id} input prices {price_input}')
    try:
        prices = re.match(r'(\b[0-9]*\b[ -]\b[0-9]*\b)', price_input).group(0)
        if "-" not in prices:
            price_min = int(prices.split(" ")[0])
            price_max = int(prices.split(" ")[1])
        else:
            price_min = int(prices.split("-")[0])
            price_max = int(prices.split("-")[1])
    except AttributeError:
        msg = bot.send_message(message.from_user.id, "Ошибка. Введите корректные числа:")
        logger.info(f'User {message.chat.id} input wrong prices')
        bot.register_next_step_handler(msg, input_prices)
    except ValueError:
        msg = bot.send_message(message.from_user.id, "Ошибка. Введите корректные числа:")
        logger.info(f'User {message.chat.id} input wrong prices')
        bot.register_next_step_handler(msg, input_prices)
    else:
        if price_min > price_max:
            price_max, price_min = price_min, price_max
        bot.send_message(message.from_user.id, f"Минимальная цена {price_min}\n"
                                               f"Максимальная цена {price_max}")
        Data_Base.add_info(column="price_min", value=price_min, user_id=message.chat.id)
        Data_Base.add_info(column="price_max", value=price_max, user_id=message.chat.id)
        logger.info(f'User {message.chat.id} add prices to DataBase')
        msg = bot.send_message(message.chat.id, f"Введите минимальную и "
                                                     f"максимальную удаленность отеля от центра города в км")
        bot.register_next_step_handler(msg, input_distance)

@logger.catch
def input_distance(message: types.Message):
    """
    Принимает на вход максимальное и минимальное расстояние от ценрта.
    Обрабатывает на ошибки и записывает в базу данных.
    Переходит в функцию ввода расстояния от центра города.

    :param message:  Принимает на вход максимальное и минимальное расстояние.
    """
    distance_input = message.text
    logger.info(f'User {message.chat.id} input distance {distance_input}')
    try:
        distances = re.match(r'(\b[0-9]*\b[ -]\b[0-9]*\b)', distance_input).group(0)
        if "-" not in distances:
            distance_min = int(distances.split(" ")[0])
            distance_max = int(distances.split(" ")[1])
        else:
            distance_min = int(distances.split("-")[0])
            distance_max = int(distances.split("-")[1])
    except AttributeError:
        msg = bot.send_message(message.from_user.id, "Ошибка. Введите корректные числа:")
        logger.info(f'User {message.chat.id} input wrong distance')
        bot.register_next_step_handler(msg, input_distance)
    except ValueError:
        msg = bot.send_message(message.from_user.id, "Ошибка. Введите корректные числа:")
        logger.info(f'User {message.chat.id} input wrong distance')
        bot.register_next_step_handler(msg, input_distance)
    else:
        if distance_min > distance_max:
            distance_max, distance_min = distance_min, distance_max
        bot.send_message(message.from_user.id, f"Минимальная удаленность: {distance_min}км\n"
                                               f"Максимальная удаленность: {distance_max}км")
        Data_Base.add_info(column="distance_min", value=distance_min, user_id=message.chat.id)
        Data_Base.add_info(column="distance_max", value=distance_max, user_id=message.chat.id)
        logger.info(f'User {message.chat.id} add distance to DataBase')
        bot.send_message(message.from_user.id, f'Введите дату заезда')
        get_date(message)


@logger.catch
def get_date(message: types.Message):
    """
    Создает календарь-клавиатуру, отправляемую пользователю.

    :param message: message: types.Message
    :return:
    """
    calendar, step = DetailedTelegramCalendar(locale='ru', min_date=datetime.date.today()).build()
    bot.send_message(message.chat.id,
                     f"Год",
                     reply_markup=calendar)

@logger.catch
@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(call: types.CallbackQuery):
    """
    Принимает действия с календарь-клавиатурой и обрабатывает введенную информацию. Записывает введенную информацию
    в базу данных. Переходит в функцию ввода количесвта выводимых отелей.

    :param call: types.CallbackQuery  Принимает действия с календарь-клавиатурой
    :return:
    """
    result, key, step = DetailedTelegramCalendar(locale='ru', min_date=datetime.date.today()).process(call.data)
    if not result and key:
        if LSTEP[step] == "month":
            inp_info = "Месяц"
        elif LSTEP[step] == "day":
            inp_info = "День"
        bot.edit_message_text(f"{inp_info}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.delete_message(chat_id=int(call.message.chat.id), message_id=call.message.message_id)
        if Data_Base.show_info(call.message.chat.id)[6] == 'None':
            bot.send_message(call.message.chat.id,
                                  f"Дата заезда {result}")
            Data_Base.add_info(column="checkIn_date", value=str(result), user_id=call.message.chat.id)
            bot.send_message(call.message.chat.id, f'Введите дату отъезда')
            get_date(call.message)
        elif Data_Base.show_info(call.message.chat.id)[7] == 'None' \
                and datetime.datetime.\
                strptime(Data_Base.show_info(call.message.chat.id)[6], "%Y-%m-%d").date() >= result:
            bot.send_message(call.message.chat.id, f'Нельзя уехать раньше, чем приехали!\n'
                                                   f' Введите другую дату отъезда')
            get_date(call.message)
        else:
            bot.send_message(call.message.chat.id,
                             f"Дата заезда {Data_Base.show_info(call.message.chat.id)[6]}\n"
                             f"Дата отъезда {result}")
            Data_Base.add_info(column="checkOut_date", value=str(result), user_id=call.message.chat.id)
            logger.info(f'User {call.message.chat.id} add date to DataBase')
            msg = bot.send_message(call.message.chat.id, f"Введите количество отелей для показа (максимум 25)")
            bot.register_next_step_handler(msg, input_hotel_count)


@logger.catch
def input_hotel_count(message: types.Message):
    """
    Принимает на вход сообщение от пользователя с количеством отелей. Обрабатывает на ошибки.
    Записывает введенную информацию в базу данных. Создает клавиатуру с вопросом о ввыводе фотографий.
    Переходит в обработку принятых с клавиатуры данных.

    :param message: types.Message  Принимает на вход сообщение от пользователя с количеством отелей
    """
    hotel_count = message.text
    logger.info(f'User {message.chat.id} input hotels {hotel_count}')
    try:
        hotels = int(re.match(r'\b[0-9]*\b', hotel_count).group(0))
    except AttributeError:
        msg = bot.send_message(message.from_user.id, "Ошибка. Введите корректное число:")
        logger.info(f'User {message.chat.id} input wrong number')
        bot.register_next_step_handler(msg, input_hotel_count)
    except ValueError:
        msg = bot.send_message(message.from_user.id, "Ошибка. Введите корректное число:")
        logger.info(f'User {message.chat.id} input wrong number')
        bot.register_next_step_handler(msg, input_hotel_count)
    else:
        if (1 > hotels) or (hotels > 25):
            msg = bot.send_message(message.from_user.id, "Ошибка! Введите число от 1 до 25")
            logger.info(f'User {message.chat.id} input wrong number')
            bot.register_next_step_handler(msg, input_hotel_count)
        else:
            Data_Base.add_info(column="hotel_count", value=hotels, user_id=message.chat.id)
            logger.info(f'User {message.chat.id} add number of hotels in DataBase')
            bot.send_message(message.from_user.id, f"Будет выведено отелей: {hotels} ")
            keyboard = types.InlineKeyboardMarkup()
            key_yes = types.InlineKeyboardButton(text='Да', callback_data='да')
            keyboard.add(key_yes)
            key_no = types.InlineKeyboardButton(text='Нет', callback_data='нет')
            keyboard.add(key_no)
            question = 'Хотите увидеть фотографии отелей?'
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)






@bot.callback_query_handler(func= types.InlineKeyboardButton)
def callback_photo(call: types.CallbackQuery):
    """
    Обрабатывает данные с клавиатуры.
    При положительном ответе переходит в функцию вопроса о количестве фотографий, иначе выводит отели.
    :param call: types.CallbackQuery  Данные с клавиатуры
    :return:
    """
    if call.data == "да":
        bot.delete_message(chat_id=int(call.message.chat.id), message_id=call.message.message_id)
        logger.info(f'User {call.message.chat.id} want to see the photos')
        msg = bot.send_message(call.message.chat.id, 'Сколько фотографий вывести?')
        bot.register_next_step_handler(msg, get_photo_count)
    elif call.data == "нет":
        info = Data_Base.show_info(call.message.chat.id)
        Data_Base.add_info(column="photo_count", value=0, user_id=call.message.chat.id)
        logger.info(f'User {call.message.chat.id} dont want see the photos')
        if info[1] in ["highprice", 'lowprice']:
            hotels = highprice_lowprice.hotelsFinder(info)
            for i in hotels:
                bot.send_message(call.message.chat.id, i, disable_web_page_preview=True)
                time.sleep(1)
            help_message(call)
        elif info[1] in ['bestdeal']:
            hotels = bestdeal.hotelsFinder(info)
            for i in hotels:
                bot.send_message(call.message.chat.id, i, disable_web_page_preview=True)
                time.sleep(1)
            help_message(call)

@logger.catch
def get_photo_count(message: types.Message):
    """
    Принимает на вход количество фоторгафий, обрабатывает ошибки ввода и записывает в информацию в базу данных.
    Отправляет пользователю финальную информацию по отелям с фотографиями.
    :param message: types.Message Принимает на вход количество фоторгафий.
    """
    count = message.text
    if count.isdigit() != True:
        msg = bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(msg, get_photo_count)
    elif (1 >= int(count)) or (int(count) > 6):
        msg = bot.send_message(message.chat.id, 'Можем вывести 2 до 6 фотографий!!')
        bot.register_next_step_handler(msg, get_photo_count)
    else:
        Data_Base.add_info(column="photo_count", value=count, user_id=message.chat.id)
        info = Data_Base.show_info(message.chat.id)
        if info[1] in ["highprice", 'lowprice']:
            hotels = highprice_lowprice.hotelsFinder(info)
            for i in hotels:
                if i[0] != None:
                    media_group=[types.InputMediaPhoto(media=url) for url in i[0]]
                    bot.send_media_group(message.chat.id, media_group)
                else:
                    bot.send_message(message.chat.id, "Нет фотографий для отеля")
                bot.send_message(message.chat.id, i[1], disable_web_page_preview=True)
                time.sleep(1)
            help_message(message)
        elif info[1] in ['bestdeal']:
            hotels = bestdeal.hotelsFinder(info)
            for i in hotels:
                if i[0] != None:
                    media_group = [types.InputMediaPhoto(media=url) for url in i[0]]
                    bot.send_media_group(message.chat.id, media_group)
                else:
                    bot.send_message(message.chat.id, "Нет фотографий для отеля")
                bot.send_message(message.chat.id, i[1], disable_web_page_preview=True)
                time.sleep(1)
            help_message(message)




@logger.catch
@bot.message_handler(commands=['history'])
def history_to_user(message: types.Message):
    """
    Активируется по команде '/history'. Отправляет пользователю его историю поиска.

    :param message: types.Message  принимает на вход '/history'.
    """
    logger.info(f'User {message.chat.id} used command "/history"')
    to_user = history.return_history(user_id=message.chat.id)

    if to_user is None:
        bot.send_message(message.from_user.id, "Вашей истории пока нет.\nПоищите отели")
        logger.info(f'User {message.chat.id} dont have history yet')
        help_message(message)
    else:
        for information in to_user:
            bot.send_message(message.from_user.id, information)
        help_message(message)

bot.polling(none_stop=True, interval=0)
