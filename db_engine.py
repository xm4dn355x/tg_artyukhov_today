# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Модуль для работы с базой данных                                                                                  #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################

from psycopg2.extras import DictCursor
import psycopg2

from bot_config import DB_NAME, DB_USERNAME, DB_PASS, DB_HOST


# DB Connection
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USERNAME, password=DB_PASS, host=DB_HOST)
cursor = conn.cursor(cursor_factory=DictCursor)


def read_db():
    """Читает все данные из базы"""
    cursor.execute('SELECT * FROM posts')
    res = cursor.fetchall()
    return res


def insert_db(row):     # STATUS FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """Вставляет в базу заготовку поста"""
    insert_statement = f"INSERT INTO posts (title, description, img, url, status) VALUES ('{row['title']}', " \
                       f"'{row['description']}', '{row['img']}', '{row['url']}', {False});"
    cursor.execute(insert_statement)
    conn.commit()
    conn.close()

def update_db(row):
    """Обновляет строку поста и ставит статус публикации True"""
    print('update_db')
    cursor.execute(f"UPDATE posts SET title='{row['title']}', description='{row['description']}', img='{row['img']}', "
                   f"status='True' WHERE url='{row['url']}'")
    conn.commit()
    conn.close()
