from create_database import Song, Playlist, create_db
from os.path import exists
# from pydub import AudioSegment
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


def create_song(path, duration, playlist_name='unknown', db_name=''):
    if db_name:
        engine = create_db(db_name)
    else:
        engine = create_db()

    if exists(path):
        # song = AudioSegment.from_mp3(path)

        original_song = EasyID3(path)
        # print(dir(original_song))
        # print(original_song.size)

        db_song = {
            'name': original_song['title'][0],
            'path': path,
            'artist': original_song['artist'][0],
            # 'length': song.duration_seconds,
            'length': duration,
            'album': original_song['album'][0]
        }

        # original_song = MP3(path)
        # song['length'] = original_song.info.length

        created_song = insert_song_into_db(engine, db_song)
        playlist_info = {
            'name': playlist_name,
            'song_id': created_song.id
        }

        insert_playlist_into_db(engine, playlist_info)
    else:
        raise Exception('There is not such file or directory! Try another one')


def get_songs(engine, name):
    session = Session(bind=engine)
    # all_songs = session.query(Song).all()
    # print(all_songs)
    return session.query(Song).filter(Song.name == name).all()


def update_song_id3(engine, song_name, new_name='', new_artist='',
                    new_album=''):
    session = Session(bind=engine)
    song = session.query(Song).filter(Song.name == song_name)
    updated = {}

    if new_name:
        updated['name'] = new_name
    if new_artist:
        updated['artist'] = new_artist
    if new_album:
        updated['album'] = new_album
    song.update(updated)
    session.commit()


def get_playlist(engine, playlist_name):
    session = Session(bind=engine)
    return session.query(Playlist).filter(Playlist.name == playlist_name).one()
