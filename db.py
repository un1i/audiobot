import sqlite3


def ensure_connection(func):

    def inner(*args, **kwargs):
        with sqlite3.connect('audio_information.db') as conn:
            res = func(*args, conn=conn, **kwargs)
            return res
    return inner


@ensure_connection
def init_db(conn, force: bool = False):
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS audio')
    c.execute('''
        CREATE TABLE IF NOT EXISTS audio (
            id INTEGER PRIMARY KEY,
            youtube_id NCHAR NOT NULL UNIQUE,
            telegram_id NCHAR NOT NULL UNIQUE
        )
    ''')
    conn.commit()


@ensure_connection
def add_new_audio(conn, youtube_id, telegram_id):
    c = conn.cursor()
    c.execute('INSERT INTO audio (youtube_id, telegram_id) VALUES (?,?)', (youtube_id, telegram_id))
    conn.commit()


@ensure_connection
def get_telegram_id(conn, youtube_id):
    c = conn.cursor()
    c.execute('SELECT telegram_id FROM audio WHERE youtube_id = ?', (youtube_id,))
    res = c.fetchone()
    if res:
        return res[0]
    return None
