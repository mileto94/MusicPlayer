# MusicPlayer

#### This is music player application written in Python for Python course 2015 in FMI.

Using this fancy app you can listen music songs, edit their metadata, get more ingo about them. Only with one click you can create playlists, adding all of your favourite songs to one place.

> *Behind the scenes this app gets name of file and checks if it exists. If yes, than it gets
 its metadata such as artist, length, format(mp3, mp4, wav and etc) and alows user to change some of them. Then the app gets abspath of converted file and saves it to **sqllite3** db called music_player
. When starting the player for the first time, it creates new hidden folder in its folder where it saves converted songs to .wav files via pydub lib.
When user wants to play song, the song will be played from the hidden folder.*


**MusicPlayer** uses **pyQt** for GUI. ORM in Python via **SQLAlchemy**. For playing files the app uses **pyglet**.

License
----

MIT