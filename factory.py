from create_database import Song, create_db
from os.path import abspath, exists
from pydub import AudioSegment
from sqlalchemy.orm import Session


def insert_into_db(engine, song_info):
    # Session is our Data Mapper
    session = Session(bind=engine)

    song = Song(
        name=song_info['name'], path=song_info['path'],
        artist=song_info['artist'], length=song_info['length'])
    session.add(song)
    session.commit()


def create_song(db_name, path, name=''):
    engine = create_db(db_name)

    if exists(path):
        original_song = AudioSegment()
        song = {}
        song['name'] = 'Hollywood tonight'
        song['path'] = abspath('song.mp3')
        song['artist'] = 'Michael Jackson'
        song['length'] = 280
        insert_into_db(engine, song)
    else:
        raise Exception('There is not such file or directory! Try another one')


def main():
    create_song('music_player', '/')
    # create_song('music_player.db', 'dsf')


if __name__ == '__main__':
    main()
