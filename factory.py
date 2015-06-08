from create_database import Song, create_db
from os.path import abspath, exists
from pydub import AudioSegment
from sqlalchemy.orm import Session
# from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3


def insert_song_into_db(engine, song_info):
    # Session is our Data Mapper
    session = Session(bind=engine)

    song = Song(
        name=song_info['name'],
        path=song_info['path'],
        artist=song_info['artist'],
        length=song_info['length'],
        album=song_info['album']
    )
    session.add(song)
    session.commit()


def create_song(db_name, path, name=''):
    folder, engine = create_db(db_name)

    if exists(path):
        old_song = AudioSegment.from_mp3(path)
        song_name = '{}.wav'.format(path.split('.')[0])
        converted_song = old_song.export(song_name, format='wav')

        original_song = EasyID3(path)
        song = {}
        song['name'] = original_song['title'][0]
        song['path'] = abspath('{}.wav'.format(song_name))
        song['artist'] = original_song['artist'][0]
        # song['length'] = original_song.info.length
        song['length'] = old_song.duration_seconds
        song['album'] = original_song['album'][0]
        insert_song_into_db(engine, song)
    else:
        raise Exception('There is not such file or directory! Try another one')


def main():
    create_song('music_player', 'song.mp3')
    # create_song('music_player.db', 'dsf')


if __name__ == '__main__':
    main()
