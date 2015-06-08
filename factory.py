from create_database import Song, Playlist, create_db
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
    return song


def insert_playlist_into_db(engine, playlist_info):
    session = Session(bind=engine)

    if session.query(Playlist).filter(
            Playlist.name == playlist_info['name']).all():
        playlist = session.query(Playlist).filter(
            Playlist.name == playlist_info['name']).all()
    else:
        playlist = Playlist(
            name=playlist_info['name'],
            song_id=playlist_info['song_id'],

        )
        session.add(playlist)
        session.commit()
    return playlist


def create_song(db_name, path, name='', playlist_name='unknown'):
    folder, engine = create_db(db_name)

    if exists(path):
        old_song = AudioSegment.from_mp3(path)
        song_name = '{}.wav'.format(path.split('.')[0])
        # converted_song = old_song.export(song_name, format='wav')

        original_song = EasyID3(path)

        song = {
            'name': original_song['title'][0],
            'path': abspath(song_name),
            'artist': original_song['artist'][0],
            'length': old_song.duration_seconds,
            'album': original_song['album'][0]
        }
        # original_song = MP3(path)
        # song['length'] = original_song.info.length

        created_song = insert_song_into_db(engine, song)
        playlist_info = {
            'name': playlist_name,
            'song_id': created_song.id
        }

        insert_playlist_into_db(engine, playlist_info)
    else:
        raise Exception('There is not such file or directory! Try another one')


def main():
    create_song('music_player', 'song.mp3', playlist_name='my_playlist')
    # create_song('music_player.db', 'dsf')


if __name__ == '__main__':
    main()
