import telebot
import yt_dlp
import os
from pydub import AudioSegment
from config import token, save_path
import requests
import time
from db import init_db, add_new_audio, get_telegram_id


def check_audio_in_db(link):
    with yt_dlp.YoutubeDL() as ydl:
        youtube_id = ydl.extract_info(link, download=False)['id']
        telegram_id = get_telegram_id(youtube_id=youtube_id)
    return telegram_id


def change_audio_name(title, id):
    sym = ('/', '\\', '*', '"', ':', '?', '|', '<', '>')
    for s in sym:
        title = title.replace(s, '')
    os.rename(save_path + id + '.m4a', save_path + title + '.m4a')
    return title


def get_audio(link):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': save_path + '%(id)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        audio_information = ydl.extract_info(link, download=True)
        title = audio_information['title']
        youtube_id = audio_information['id']
        title = change_audio_name(title, youtube_id)
        path = save_path + title + '.m4a'
        audio_size = os.stat(path).st_size
        if audio_size > 50*1024*1024:
            audio = AudioSegment.from_file(path)
            audio.export(path, bitrate='64k')
        res = (title, youtube_id)
    return res


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
                    audio = open(save_path + title + '.m4a', 'rb')
                    try:
                        print('отправляем сообщение')
                        telegram_id = bot.send_audio(message.chat.id, audio).audio.file_id
                        add_new_audio(youtube_id=youtube_id, telegram_id=telegram_id)
                    except Exception as ex:
                        raise
                    finally:
                        audio.close()
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


