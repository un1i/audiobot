import yt_dlp
from pydub import AudioSegment
from db import get_telegram_id
from config import save_path
import os


def check_audio_in_db(link):
    with yt_dlp.YoutubeDL() as ydl:
        youtube_id = ydl.extract_info(link, download=False)['id']
        telegram_id = get_telegram_id(youtube_id=youtube_id)
    return telegram_id


def get_audio(link):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': save_path + '%(id)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        audio_information = ydl.extract_info(link, download=True)
        title = audio_information['title']
        youtube_id = audio_information['id']
        path = save_path + youtube_id + '.m4a'
        audio_size = os.stat(path).st_size
        if audio_size > 50*1024*1024:
            audio = AudioSegment.from_file(path)
            audio.export(path, bitrate='64k')
        res = (title, youtube_id)
    return res
