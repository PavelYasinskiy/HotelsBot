import datetime

from dbase import data_base


def add_history(info: list, names: list) -> None:
    """
    Получает доступ к базе данных и
    добавляет информацию о команде, отелях и времени поиска пользователем.

    :param info: list информация о пользоваеле из Базы Данных
    :param names: list Названия отелей
    """
    user_info = info
    hotel_names = names
    time = (" ").join((datetime.datetime.now().isoformat(timespec='seconds')).split("T"))
    if user_info[12] in [None, 'None']:
        history_adding = f" разделитель Команда: {user_info[1]}" \
                         f" разделитель Дата и время: {time}" \
                         f" разделитель {('Отель: ').join(hotel_names)}"
    else:
        user_info[12] += f" разделитель Команда: {user_info[1]} " \
                         f" разделитель Дата и время: {time} " \
                         f" разделитель {('Отель: ').join(hotel_names)}"
        history_adding = user_info[12]
    data_base.add_info(column="history", value=history_adding, user_id=int(user_info[0]))


def return_history(user_id: int) -> list or None:
    """
    Получает доступ к базе данных и
    возвращает список информации о команде, отелях и времени поиска пользователем.

    :param user_id: int Пользовательский ID
    :return: list История поиска пользователя
    """
    try:
        history = data_base.show_info(user_id=user_id)[12]
        history_clean = history.split(' разделитель ')
        history_clean.remove("")
        counter = 0
        output = []
        string_to_add = ""
        for i in history_clean:
            counter += 1
            if counter != 3:
                string_to_add += (f'{i}\n')
            else:
                counter = 0
                hotels = i.split("Отель:")
                for j in hotels:
                    counter += 1
                    string_to_add += (f'{counter}: {j}\n')
                counter = 0
                output.append(string_to_add)
                string_to_add = ""
    except TypeError:
        output = None
    return output
