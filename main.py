# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Парсер новостных сайтов, который отправляет посты в телеграм-канал Артюхов-today                                  #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


from time import sleep
import threading

from telegram import Bot
from telegram.ext import Updater
from telegram.utils.request import Request

from bot_config import ADMIN_ID, API_TOKEN, CHAT_ID
from db_engine import update_db
from news_parser import parse_all


req = Request(connect_timeout=3)
bot = Bot(request=req, token=API_TOKEN)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher


def log_error(f):
    """Отлавливание ошибок"""
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error = f'ERROR {e} in '
            print(error)
            update = args[0]
            if update and hasattr(update, 'message'):
                update.message.bot.send_message(chat_id=ADMIN_ID, text=error)
            raise e
    return inner


def update_channel_loop():
    data_list = parse_all()
    for data in data_list:
        print(data)
        post_in_channel(data)
        update_db(data)
        sleep(1)
    threading.Timer(120, update_channel_loop).start()


@log_error
def post_in_channel(data: dict) -> None:
    """Постит пост в канал"""
    bot.send_message(
        parse_mode='markdown',
        chat_id=CHAT_ID,
        text=f"**{data['title']}**\n{data['description']}\n{data['url']}"
    )


if __name__ == '__main__':
    print('Артюхов-Today')
    update_channel_loop()

# docker build -t artyuhov_today .
# docker run --network host artyuhov_today