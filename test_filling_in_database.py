import unittest
from os import remove
from sqlalchemy.orm import Session

from create_database import create_db, Song, Playlist
from factory import (
    get_songs, insert_song_into_db, insert_playlist_into_db, get_playlist,
    create_song, update_song_id3)


class TestCreateDb(unittest.TestCase):
    def setUp(self):
        self.engine = create_db('test_db')
        self.song_info = {
            'name': 'song_name',
            'path': '/home/user/song.mp3',
            'artist': 'artist_name',
            'length': 3.46,
            'album': 'album_name'
        }
        self.song = Song(
            name=self.song_info['name'],
            path=self.song_info['path'],
            artist=self.song_info['artist'],
            length=self.song_info['length'],
            album=self.song_info['album'])

        self.playlist_info = {
            'name': 'test_playlist',
            'song_id': 1
        }

        self.playlist = Playlist(
            name=self.playlist_info['name'],
            song_id=self.playlist_info['song_id'])

    def tearDown(self):
        remove('test_db.db')

    def test_song_str_method(self):
        expected = '{0} - {1} ({2})'.format(
            self.song.artist, self.song.name, self.song.length)
        self.assertEqual(str(self.song), expected)

    def test_playlist_str_method(self):
        expected = '{0}'.format(self.playlist.name)
        self.assertEqual(str(self.playlist), expected)

    def test_insert_song_into_db_one_object(self):
        insert_song_into_db(self.engine, self.song_info)
        result = get_songs(self.engine, 'song_name')
        expected = [self.song]
        self.assertEqual(result, expected)

    def test_insert_song_into_db_two_objects(self):
        insert_song_into_db(self.engine, self.song_info)
        insert_song_into_db(self.engine, self.song_info)
        result = get_songs(self.engine, 'song_name')
        expected = [self.song] * 2
        self.assertEqual(result, expected)

    def test_insert_playlist_into_db_one_object(self):
        insert_playlist_into_db(self.engine, self.playlist_info)
        result = [get_playlist(self.engine, 'test_playlist')]
        expected = [self.playlist]
        self.assertEqual(result, expected)

    def test_insert_playlist_into_db_five_objects(self):
        for _ in range(5):
            insert_playlist_into_db(self.engine, self.playlist_info)
        result = [get_playlist(self.engine, 'test_playlist')]
        expected = [self.playlist]
        self.assertEqual(result, expected)

    def test_create_song_with_valid_file_path(self):
        create_song('song.mp3', 3.22, playlist_name='my_playlist',
                    db_name='test_db')
        session = Session(bind=self.engine)
        all_songs = session.query(Song).all()
        all_playlists = session.query(Playlist).all()
        self.assertEqual(len(all_songs), 1)
        self.assertEqual(len(all_playlists), 1)

    def test_create_song_with_invalid_file_path(self):
        with self.assertRaises(Exception):
            create_song('Asong.mp3', 3.22, playlist_name='my_playlist',
                        db_name='test_db')

    def test_update_song_id3(self):
        insert_song_into_db(self.engine, self.song_info)
        update_song_id3(
            self.engine,
            self.song_info['name'],
            new_name='test',
            new_artist='Pesho',
            new_album='2003')
        songs = get_songs(self.engine, 'test')
        self.song.name = 'test'
        self.song.artist = 'Pesho'
        self.song.album = '2003'
        self.assertEqual([self.song], songs)

    def test_update_song_id3_with_wrong_params(self):
        insert_song_into_db(self.engine, self.song_info)
        name = self.song_info['name']
        update_song_id3(
            self.engine,
            name,
            'Pesho',
            '2003')
        songs = get_songs(self.engine, name)
        self.assertEqual([], songs)


if __name__ == '__main__':
    unittest.main()
