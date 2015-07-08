# MusicPlayer

#### This is music player application written in Python for Python course 2015 in FMI.

Using this fancy app you can listen music songs, edit their metadata, get more ingo about them. Only with one click you can create playlists, adding all of your favourite songs to one place.

> Behind the scenes this app gets name of file and checks if it exists. If yes, than it gets
 its metadata such as artist, length, format(mp3, mp4, wav and etc) and alows user to change some of them. Then the app gets abspath of converted file and saves it to* **sqllite3** *db called music_player
. When starting the player for the first time, it creates new hidden folder in its folder where it saves converted songs to .wav files via pydub lib.
When user wants to play song, the song will be played from the hidden folder.

### Future plans
This app will be like library - it could be used both as terminal and desktop application. The point is to separate logic from GUI in order to be reusable.
GUI will have main sreen with buttons for play, pause, stop, previous, next and repeat song. It will show artist, song's name, song's length and current seconds of playing the file. There will be clock with real time and button for raising up or slowing down the volume. Probably the app will be able to visualize some kind of video files.


**MusicPlayer** uses **pyQt** for GUI. ORM in Python via **SQLAlchemy**. For playing files the app uses **pyglet**.

Short links of used libs for music:
 - [pyglet] - play music
 - [mutagen] - get files' metadata
 - [pydub] - convert files to .wav

 
#### Requires
ffmpeg, which is available after **sudo apt-get install libav-tools** in OS X.


#### Installation:
 - sudo apt-get install python3.4-dev
 - sudo apt-get install build-essential
 - sudo apt-get install qt4-dev-tools libqt4-dev libqt4-core libqt4-gui
 - unpack sip and pyqt
 - $ cd ~/sip-some-version 
 - python3.4 configure.py
 - sudo make # installs sip package
 - sudo make install
 - $ cd ~/pyqt-directory
 - sudo python3.4 configure.py
 - sudo make # installs qt package
 - sudo make install
 

License
----

MIT

[mutagen]:https://mutagen.readthedocs.org/en/latest/tutorial.html
[pyglet]:https://pyglet.readthedocs.org/en/pyglet-1.2-maintenance/programming_guide/quickstart.html#mp3
[pydub]:http://pydub.com/
