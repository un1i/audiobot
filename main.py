import telebot
import os
import requests
import time
from audio import check_audio_in_db, get_audio
from config import token, save_path
from db import init_db, add_new_audio


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def strart_message(message):
        bot.send_message(message.chat.id, "Привет, я бот, который отделяет звук от видео и присылает его тебе аудио файлом. Просто отправь мне ссылку на youtube видео и получишь аудио файл")

    @bot.message_handler(content_types=['text'])
    def send_audio(message):
        time_start = time.time()
        try:
            requests.head(message.text)
            try:
                message_id = bot.send_message(message.chat.id, 'Пожалуйста подождите, аудиозапись загружается.').message_id
                telegram_id = check_audio_in_db(message.text)
                if telegram_id:
                    bot.send_audio(message.chat.id, telegram_id)
                else:
                    title, youtube_id = get_audio(message.text)
                    path = save_path + youtube_id + '.m4a'
                    audio = open(path, 'rb')
                    try:
                        telegram_id = bot.send_audio(message.chat.id, audio, title=title, performer='@Audio78_bot', timeout=60).audio.file_id
                        add_new_audio(youtube_id=youtube_id, telegram_id=telegram_id)

                    except Exception as ex:
                        raise
                    finally:
                        audio.close()
                        os.remove(path)
            except Exception as ex:
                print(ex)
                bot.send_message(message.chat.id, "Что-то пошло не так...")
            finally:
                bot.delete_message(message.chat.id, message_id)
        except Exception as ex:
            bot.send_message(message.chat.id, "Вы ввели недействительную ссылку.")
        time_end = time.time()
        print(time_end-time_start)

    bot.polling()


if __name__ == '__main__':
    telegram_bot(token)
    init_db(force=True)


