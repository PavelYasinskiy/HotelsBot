import sqlite3

from loguru import logger


@logger.catch
def create_info(user_id: int) -> None:
    """
    Создает базу данных и добавляет пользователя.

    :param user_id: int пользовательский id
    """

    with sqlite3.connect("dbase/users_data.db") as user_data:
        cur = user_data.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER UNIQUE,
                                                        command TEXT,
                                                        city_ID INTEGER,
                                                        city_name TEXT,
                                                        price_min INTEGER,
                                                        price_max INTEGER,
                                                        checkIn_date TEXT,
                                                        checkOut_date TEXT,
                                                        distance_min INTEGER,
                                                        distance_max INTEGER,
                                                        hotel_count INTEGER,
                                                        photo_count INTEGER,
                                                        history TEXT
                                                        )""")
        try:
            cur.execute(f'''INSERT INTO users(user_id) VALUES({user_id})''')
            logger.info(f'User {user_id} create DataBase')
        except sqlite3.IntegrityError:
            pass
        finally:
            user_data.commit()


@logger.catch()
def add_info(column: str, value: any, user_id: int) -> None:
    """
    Добавляет в базу данных информацию пользователя.

    :param column: str Колонка в которую добавляем информацию
    :param value: any Новое значение колонки
    :param user_id: int Пользовательский ID
    """
    with sqlite3.connect('dbase/users_data.db') as user_data:
        cur = user_data.cursor()
        cur.execute(f"""UPDATE users SET {column} = ? WHERE user_id = ?""", (value, user_id))
        user_data.commit()


@logger.catch()
def show_info(user_id: int) -> list:
    """
    Возвращает список доступной информации по пользователю.
    :param user_id: int Пользовательский ID
    :return: list [command,city_ID,city_name,price_min,price_max,checkIn_date,checkOut_date,distance_min
     distance_max,hotel_count, photo_count, history ]
    """
    with sqlite3.connect('dbase/users_data.db') as user_data:
        cur = user_data.cursor()
        cur.execute(f"""SELECT * FROM users WHERE user_id = {user_id}""")
        ret = cur.fetchall()
        fun = list(map(lambda x: str(x), ret[0]))
        return fun
