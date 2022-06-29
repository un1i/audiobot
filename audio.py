import yt_dlp
from pydub import AudioSegment
from db import get_telegram_id
from config import save_path
import math


def check_audio_in_db(link):
    with yt_dlp.YoutubeDL() as ydl:
        youtube_id = ydl.extract_info(link, download=False)['id']
        telegram_id = get_telegram_id(youtube_id=youtube_id)
    return telegram_id


def change_bitrate(audio_size, path):
    k = math.ceil(audio_size / (50*1024*1024))
    new_bitrate = 128000 // (k*1000)
    audio = AudioSegment.from_file(path)
    new_bitrate = str(new_bitrate) + 'k'
    audio.export(path, bitrate=new_bitrate)


def get_audio(link):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': save_path + '%(id)s.%(ext)s',
    }
    telegram_size_limit = 50 * 1024 * 1024
    bot_size_limit = 300 * 1024 * 1024
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        audio_information = ydl.extract_info(link, download=False)
        size = audio_information['filesize']
        if size > bot_size_limit:
            return None, None
        ydl.download(link)
        title = audio_information['title']
        youtube_id = audio_information['id']
        path = save_path + youtube_id + '.m4a'
        if size > telegram_size_limit:
            change_bitrate(size, path)
    res = (title, youtube_id)
    return res
