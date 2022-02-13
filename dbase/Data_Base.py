import sqlite3
from loguru import logger
import os
@logger.catch
def create_info(user_id: int):

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
def add_info(column, value, user_id):
    with sqlite3.connect('dbase/users_data.db') as user_data:
        cur = user_data.cursor()
        cur.execute(f"""UPDATE users SET {column} = ? WHERE user_id = ?""", (value, user_id))
        user_data.commit()

@logger.catch()
def show_info(user_id):
    with sqlite3.connect('dbase/users_data.db') as user_data:
        cur = user_data.cursor()
        cur.execute(f"""SELECT * FROM users WHERE user_id = {user_id}""")
        ret = cur.fetchall()
        fun = list(map(lambda x: str(x), ret[0]))
        return fun
