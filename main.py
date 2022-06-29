import telebot
import os
import requests
import time
from audio import check_audio_in_db, get_audio
from config import token, save_path
from db import init_db, add_new_audio
from bot_msg import *


def telegram_bot():
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, msg_start)

    @bot.message_handler(content_types=['text'])
    def send_audio(message):
        time_start = time.time()

        try:
            requests.head(message.text)
            message_id = bot.send_message(message.chat.id, msg_load).message_id
            try:
                telegram_id = check_audio_in_db(message.text)
                if telegram_id:
                    bot.send_audio(message.chat.id, telegram_id)
                else:
                    title, youtube_id = get_audio(message.text)
                    if title is None:
                        bot.send_message(message.chat.id, msg_size_error)
                    else:
                        path = save_path + youtube_id + '.m4a'
                        audio = open(path, 'rb')
                        try:
                            telegram_id = bot.send_audio(message.chat.id, audio, title=title, timeout=60).audio.file_id
                            add_new_audio(youtube_id=youtube_id, telegram_id=telegram_id)
                        except Exception:
                            raise
                        finally:
                            audio.close()
                            os.remove(path)
            except Exception as ex:
                print(ex)
                bot.send_message(message.chat.id, msg_error)
            finally:
                bot.delete_message(message.chat.id, message_id)
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, msg_invalid_url)

        time_end = time.time()
        print(time_end - time_start)

    bot.polling()


if __name__ == '__main__':
    telegram_bot()
    init_db(force=True)

