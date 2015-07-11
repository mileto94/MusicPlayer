from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship

# base table from which declare own tables
BaseTable = declarative_base()


class Song(BaseTable):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    artist = Column(String)  # nullable=True
    length = Column(Integer)
    album = Column(String)  # null=True

    def __str__(self):
        return '{0} - {1} ({2})'.format(self.artist, self.name, self.length)

    # when using console
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.name == other.name and self.path == other.path and
                self.artist == other.artist and self.length == other.length and
                self.album == other.album)


class Playlist(BaseTable):
    __tablename__ = 'playlist'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    song_id = Column(Integer, ForeignKey('song.id'))
    song = relationship('Song', backref='playlists')

    def __str__(self):
        return '{0}'.format(self.name)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.name == other.name and self.song_id == other.song_id
                and self.song == other.song)


def create_db(db_name='music_player'):
    engine = create_engine('sqlite:///{0}.db'.format(db_name))

    # create all tables
    BaseTable.metadata.create_all(engine)
    return engine
