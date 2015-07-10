import sys
from PyQt5 import Qt, QtCore
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist


class Controllers(Qt.QWidget):
    play = Qt.pyqtSignal()
    pause = Qt.pyqtSignal()
    stop = Qt.pyqtSignal()
    next = Qt.pyqtSignal()
    previous = Qt.pyqtSignal()
    changeVolume = Qt.pyqtSignal(int)
    changeMuting = Qt.pyqtSignal(bool)
    changeSpeed = Qt.pyqtSignal(float)

    def __init__(self, parent=None):
        super(Controllers, self).__init__(parent)

        # player initial state
        self.playerState = QMediaPlayer.StoppedState
        self.playerMuted = False

        # create playButton
        self.playButton = Qt.QToolButton(clicked=self.playAction)
        self.playButton.setIcon(self.style().standardIcon(
            Qt.QStyle.SP_MediaPlay))

        # create stopButton
        self.stopButton = Qt.QToolButton(clicked=self.stop)
        self.stopButton.setIcon(self.style().standardIcon(
            Qt.QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)

        # create nextButton
        self.nextButton = Qt.QToolButton(clicked=self.next)
        self.nextButton.setIcon(self.style().standardIcon(
            Qt.QStyle.SP_MediaSkipForward))

        # create previousButton
        self.previousButton = Qt.QToolButton(clicked=self.previous)
        self.previousButton.setIcon(self.style().standardIcon(
            Qt.QStyle.SP_MediaSkipBackward))

        # create muteButton
        self.muteButton = Qt.QToolButton(clicked=self.muteAction)
        self.muteButton.setIcon(self.style().standardIcon(
            Qt.QStyle.SP_MediaVolume))

        # create volumeSlider
        self.volumeSlider = Qt.QSlider(
            QtCore.Qt.Horizontal, sliderMoved=self.changeVolume)
        self.volumeSlider.setRange(0, 100)

        # create speedComboBox
        self.speedComboBox = Qt.QComboBox(activated=self.updateSpeed)
        self.speedComboBox.addItem('0.5x', 0.5)
        self.speedComboBox.addItem('1.0x', 1.0)
        self.speedComboBox.addItem('2.0x', 2.0)
        self.speedComboBox.setCurrentIndex(1)

        # create layout
        layout = Qt.QHBoxLayout()
        layout.setContentsMargins(30, 0, 0, 0)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.muteButton)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(self.speedComboBox)
        self.setLayout(layout)

    def playAction(self):
        if self.playerState in [
                QMediaPlayer.StoppedState, QMediaPlayer.PausedState]:
            self.play.emit()
        elif self.playerState == QMediaPlayer.PlayingState:
            self.pause.emit()

    def muteAction(self):
        self.changeMuting.emit(not self.playerMuted)

    def getPlaybackSpeed(self):
        return self.speedComboBox.itemData(self.speedComboBox.currentIndex())

    def setPlaybackSpeed(self, speed):
        for i in range(self.speedComboBox.count()):
            if QtCore.qFuzzyCompare(speed, self.speedComboBox.itemData(i)):
                self.speedComboBox.setCurrentIndex(i)
                return
        self.speedComboBox.addItem('{0}x'.format(speed), speed)
        self.speedComboBox.setCurrentIndex(self.speedComboBox.count() - 1)

    def updateSpeed(self):
        self.changeSpeed.emit(self.getPlaybackSpeed())

    # changeVolume, changeSpeed, next, previous - come from super

    def getVolume(self):
        return self.volumeSlider.value()

    def setVolume(self, volume):
        self.volumeSlider.setValue(volume)

    def isMuted(self):
        return self.playerMuted

    def setMuted(self, muted):
        if muted == self.playerMuted:
            return

        self.playerMuted = muted
        self.muteButton.setIcon(self.style().standardIcon(
            Qt.QStyle.SP_MediaVolumeMuted if muted
            else Qt.QStyle.SP_MediaVolume))

    def getState(self):
        return self.playerState

    def setState(self, state):
        if state == self.playerState:
            return

        self.playerState = state

        if state == QMediaPlayer.StoppedState:
            self.stopButton.setEnabled(False)
            self.playButton.setIcon(self.style().standardIcon(
                Qt.QStyle.SP_MediaPlay))
        elif state == QMediaPlayer.PlayingState:
            self.stopButton.setEnabled(True)
            self.playButton.setIcon(self.style().standardIcon(
                Qt.QStyle.SP_MediaPause))
        elif state == QMediaPlayer.PausedState:
            self.stopButton.setEnabled(True)
            self.playButton.setIcon(self.style().standardIcon(
                Qt.QStyle.SP_MediaPlay))


class VideoWidget(Qt.QVideoWidget):
    pass


class PlaylistModel(QtCore.QAbstractItemModel):

    Title, ColumnCount = range(2)

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)

        self.music_playlist = None

    def rowCount(self, parent=Qt.QModelIndex()):
        if self.music_playlist is not None and not parent.isValid():
            return self.music_playlist.mediaCount()
        return 0

    def columnCount(self, parent=Qt.QModelIndex()):
        return self.ColumnCount if not parent.isValid() else 0

    def index(self, row, column, parent=Qt.QModelIndex()):
        if (self.music_playlist is not None and not parent.isValid() and
            row >= 0 and row < self.music_playlist.mediaCount() and
                column >= 0 and column < self.ColumnCount):
            return self.createIndex(row, column)
        return Qt.QModelIndex()

    def parent(self, child):
        return QtCore.QModelIndex()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            if index.column() == self.Title:
                location = self.music_playlist.media(index.row()).canonicalUrl()
                return Qt.QFileInfo(location.path()).fileName()
            return self.m_data[index]

    def playlist(self):
        return self.music_playlist

    def setPlaylist(self, playlist):
        if self.music_playlist is not None:
            self.music_playlist.mediaAboutToBeInserted.disconnect(
                self.beginInsertItems)
            self.music_playlist.mediaInserted.disconnect(self.endInsertItems)
            self.music_playlist.mediaAboutToBeRemoved.disconnect(
                self.beginRemoveItems)
            self.music_playlist.mediaRemoved.disconnect(self.endRemoveItems)
            self.music_playlist.mediaChanged.disconnect(self.changeItems)

        self.beginResetModel()
        self.music_playlist = playlist

        if self.music_playlist is not None:
            self.music_playlist.mediaAboutToBeInserted.connect(
                self.beginInsertItems)
            self.music_playlist.mediaInserted.connect(self.endInsertItems)
            self.music_playlist.mediaAboutToBeRemoved.connect(
                self.beginRemoveItems)
            self.music_playlist.mediaRemoved.connect(self.endRemoveItems)
            self.music_playlist.mediaChanged.connect(self.changeItems)

        self.endResetModel()

    def beginInsertItems(self, start, end):
        # derived from super
        self.beginInsertRows(QtCore.QModelIndex(), start, end)

    def endInsertItems(self):
        # derived from super
        self.endInsertRows()

    def beginRemoveItems(self, start, end):
        # derived from super
        self.beginRemoveRows(QtCore.QModelIndex(), start, end)

    def endRemoveItems(self):
        # derived from super
        self.endRemoveRows()

    def changeItems(self, start, end):
        # derived from super
        self.dataChanged.emit(
            self.index(start, 0),
            self.index(end, self.ColumnCount))


class HistogramWidget(Qt.QWidget):
    def __init__(self, parent=None):
        super(HistogramWidget, self).__init__(parent)

    def processFrame(self, frame):
        pass


class Player(Qt.QWidget):
    """docstring for Player"""
    fullScreenChanged = Qt.pyqtSignal(bool)

    def __init__(self, playlist, parent=None):
        # create player
        super(Player, self).__init__(parent)

        self.trackInfo = ''
        self.statusInfo = ''
        self.duration = 0

        # create player object
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.metaDataChanged.connect(self.metaDataChanged)
        self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)

        self.player.mediaStatusChanged.connect(self.statusChanged)
        self.player.bufferStatusChanged.connect(self.bufferingProgress)
        # self.player.videoAvailableChanged.connect(self.videoAvailableChanged)
        self.player.error.connect(self.displayErrorMessage)

        # connect with VideoWidget
        # self.videoWidget = VideoWidget()
        # self.player.setVideoOutput(self.videoWidget)

        # connect with PlaylistModel
        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = Qt.QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(self.playlistModel.index(
            self.playlist.currentIndex(), 0))

        # change to next song
        self.playlistView.activated.connect(self.jump)

        self.slider = Qt.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, self.player.duration() / 1000)

        self.labelDuration = Qt.QLabel()
        self.slider.sliderMoved.connect(self.seek)

        # create histogram
        self.labelHistogram = Qt.QLabel()
        self.labelHistogram.setText('Histogram: ')
        self.histogram = HistogramWidget()
        histogramLayout = Qt.QHBoxLayout()
        histogramLayout.addWidget(self.labelHistogram)
        histogramLayout.addWidget(self.histogram, 1)

        # create videoProbe
        self.videoProbe = Qt.QVideoProbe()
        self.videoProbe.videoFrameProbed.connect(self.histogram.processFrame)
        self.videoProbe.setSource(self.player)

        # add control
        controls = Controllers()
        controls.setState(self.player.state())
        controls.setVolume(self.player.volume())
        controls.setMuted(controls.isMuted())

        # connect player's controls with Controllers
        controls.play.connect(self.player.play)
        controls.pause.connect(self.player.pause)
        controls.stop.connect(self.player.stop)
        controls.next.connect(self.playlist.next)
        controls.previous.connect(self.previousAction)
        controls.changeVolume.connect(self.player.setVolume)
        controls.changeMuting.connect(self.player.setMuted)
        # setPlaybackRate is from QMediaPlayer
        controls.changeSpeed.connect(self.player.setPlaybackRate)
        # controls.stop.connect(self.videoWidget.update)

        self.player.stateChanged.connect(controls.setState)
        self.player.volumeChanged.connect(controls.setVolume)
        self.player.mutedChanged.connect(controls.setMuted)

        # create fullScreenButton
        self.fullScreenButton = Qt.QPushButton('FullScreen')
        self.fullScreenButton.setCheckable(True)

        # displayLayout
        displayLayout = Qt.QHBoxLayout()
        # displayLayout.addWidget(self.videoWidget, 2)
        displayLayout.addWidget(self.playlistView)

        # controlLayout
        controlLayout = Qt.QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        # connect controlLayout with controls
        controlLayout.addWidget(controls)
        controlLayout.addStretch(1)
        # connect controlLayout with fullScreenButton
        controlLayout.addWidget(self.fullScreenButton)

        # visualize player
        layout = Qt.QVBoxLayout()
        layout.addLayout(displayLayout)

        # layout for sliding song playing
        hLayout = Qt.QHBoxLayout()
        hLayout.addWidget(self.slider)
        hLayout.addWidget(self.labelDuration)

        layout.addLayout(hLayout)
        layout.addLayout(controlLayout)
        layout.addLayout(histogramLayout)

        # set icon
        self.setWindowIcon(Qt.QIcon('favicon.ico'))

        # create menus
        toolBar = Qt.QToolBar()

        # create basic actions
        self.createActions()

        # create simpleButton
        simpleButton = Qt.QToolButton()
        simpleButton.setDefaultAction(self.simpleAct)

        # create fileButton for fileMenu
        fileButton = Qt.QToolButton()
        fileButton.setText('File')
        fileButton.setPopupMode(Qt.QToolButton.MenuButtonPopup)
        fileButton.setMenu(self.popFileMenu())

        # create editButton for editMenu
        editButton = Qt.QToolButton()
        editButton.setText('Edit')
        editButton.setPopupMode(Qt.QToolButton.MenuButtonPopup)
        editButton.setMenu(self.popEditMenu())

        # display in toolBar these buttons
        toolBar.addWidget(simpleButton)
        toolBar.addWidget(fileButton)
        toolBar.addWidget(editButton)

        # add toolBar to layout of the player
        layout.addWidget(toolBar)
        layout.addWidget(Qt.QGroupBox())

        self.setWindowTitle("Python Music Player")
        self.setLayout(layout)

        if not self.player.isAvailable():
            Qt.QMessageBox(self, 'Unavailable service')
            # self.displayErrorMessage()
            controls.setEnabled(False)
            self.playlistView.setEnabled(False)
            self.fullScreenButton.setEnabled(False)

        self.metaDataChanged()

        self.addToPlaylist(playlist)

    # create fileMenu
    def popFileMenu(self):
        aMenu = Qt.QMenu(self)
        aMenu.addAction(self.fileOpenAct)
        aMenu.addAction(self.fileCloseAct)
        return aMenu

    # create editMenu
    def popEditMenu(self):
        aMenu = Qt.QMenu(self)
        aMenu.addAction(self.editCopyAct)
        aMenu.addAction(self.filePasteAct)
        return aMenu

    def createActions(self):
        self.simpleAct = Qt.QAction('Simple', self, triggered=self.do_nothing)
        self.fileOpenAct = Qt.QAction('Open', self, triggered=self.open)
        self.fileOpenAct.setShortcut('Ctrl+O')

        self.fileCloseAct = Qt.QAction('Close', self, triggered=self.close)
        self.fileCloseAct.setShortcut('Ctrl+Q')

        self.editCopyAct = Qt.QAction('Copy', self, triggered=self.do_nothing)
        self.filePasteAct = Qt.QAction('Paste', self, triggered=self.do_nothing)

    def do_nothing(self):
        print('do nothing')

    # get and display song duration
    def durationChanged(self, duration):
        duration /= 1000

        self.duration = duration
        self.slider.setMaximum(duration)

    # change slider position
    def positionChanged(self, progress):
        progress /= 1000

        if not self.slider.isSliderDown():
            self.slider.setValue(progress)

        self.updateDurationInfo(progress)

    def updateDurationInfo(self, currentInfo):
        duration = self.duration
        if currentInfo or duration:
            currentTime = QtCore.QTime(
                (currentInfo / 3600) % 60,  # hours
                (currentInfo / 60) % 60,  # minutes
                currentInfo % 60,  # seconds
                (currentInfo * 1000) % 1000)  # miliseconds
            totalTime = QtCore.QTime(
                (duration / 3600) % 60,  # hours
                (duration / 60) % 60,  # minutes
                duration % 60,  # seconds
                (duration * 1000) % 1000)  # miliseconds
            formating = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
            toString = (currentTime.toString(formating) + ' / ' +
                        totalTime.toString(formating))
        else:
            toString = ''

        self.labelDuration.setText(toString)

    def metaDataChanged(self):
        if self.player.isMetaDataAvailable():
            self.setTrackInfo('{0} - {1}'.format(
                self.player.metaData(Qt.QMediaMetaData.AlbumArtist),
                self.player.metaData(Qt.QMediaMetaData.Title)))

    def setTrackInfo(self, info):
        self.trackInfo = info

        if self.statusInfo:
            self.setWindowTitle('{0} | {1}'.format(
                self.trackInfo, self.statusInfo))
        else:
            self.setWindowTitle(self.trackInfo)

    def playlistPositionChanged(self, position):
        self.playlistView.setCurrentIndex(
            self.playlistModel.index(position, 0))

    def statusChanged(self, status):
        self.handleCursor(status)

        if status == QMediaPlayer.LoadingMedia:
            self.setStatusInfo('Loading...')
        elif status == QMediaPlayer.StalledMedia:
            self.setStatusInfo('Media Stalled')
        elif status == QMediaPlayer.EndOfMedia:
            Qt.QApplication.alert(self)
        elif status == QMediaPlayer.InvalidMedia:
            self.displayErrorMessage()
        else:
            self.setStatusInfo('')

    def handleCursor(self, status):
        if status in [QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia,
                      QMediaPlayer.StalledMedia]:
            self.setCursor(QtCore.Qt.BusyCursor)
        else:
            self.unsetCursor()

    def setStatusInfo(self, info):
        self.statusInfo = info

        if self.statusInfo:
            self.setWindowTitle('{0} | {1}'.format(
                self.trackInfo, self.statusInfo))
        else:
            self.setWindowTitle(self.trackInfo)

    def bufferingProgress(self, progress):
        self.setStatusInfo('Buffering {0}'.format(progress))

    def displayErrorMessage(self):
        self.statusInfo(self.player.errorString())

    def jump(self, index):
        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.player.play()

    def seek(self, seconds):
        self.player.setPosition(seconds * 1000)

    def previousAction(self):
        self.playlist.previous()

    def close(self):
        choice = Qt.QMessageBox.question(
            self,
            'Close',
            'Close the app?',
            Qt.QMessageBox.Yes | Qt.QMessageBox.No)

        if choice == Qt.QMessageBox.Yes:
            sys.exit()

    def open(self):
        print('Open file')
        names, _ = Qt.QFileDialog.getOpenFileNames(self, 'Open Files')
        # ['/home/milka/Documents/MusicPlayer/song.mp3']
        self.addToPlaylist(names)

    def addToPlaylist(self, names):
        for name in names:
            fileInfo = Qt.QFileInfo(name)
            if fileInfo.exists():
                url = QtCore.QUrl.fromLocalFile(fileInfo.absoluteFilePath())
                # print(url.path())  # /home/milka/Documents/MusicPlayer/song.mp3
                # print(dir(url))
                # print(url.url())  # file:///home/milka/Documents/MusicPlayer/song.mp3
                # save_to_db song url
                # print(fileInfo.suffix())  # wav, mp3
                if fileInfo.suffix().lower() == 'm3u':
                    self.playlist.load(url)
                else:
                    self.playlist.addMedia(Qt.QMediaContent(url))
            else:
                url = QtCore.QUrl(name)
                if url.isValid():
                    self.playlist.addMedia(Qt.QMediaContent(url))

    # def videoAvailableChanged(self, available):
    #     if available:
    #         self.fullScreenButton.clicked.connect(
    #             self.videoWidget.setFullScreen)
    #         self.videoWidget.fullScreenChanged.connect(
    #             self.fullScreenButton.setChecked)

    #         if self.fullScreenButton.isChecked():
    #             self.videoWidget.setFullScreen(True)
    #     else:
    #         self.fullScreenButton.clicked.disconnect(
    #             self.videoWidget.setFullScreen)
    #         self.videoWidget.fullScreenChanged.disconnect(
    #             self.fullScreenButton.setChecked)

    #         self.videoWidget.setFullScreen(False)

    # def enlarge_window(self, state):
    #     if state == QtCore.Qt.Checked:
    #         self.setGeometry(50, 50, 1000, 600)
    #         # self.showFullScreen()
    #         # self.showMaximized()
    #     else:
    #         self.setGeometry(50, 50, 500, 300)

    # def download(self):
    #     self.completed = 0

    #     while self.completed < 100:
    #         self.completed += 0.0001
    #         self.progress.setValue(self.completed)


def run():
    app = Qt.QApplication(sys.argv)
    # label = Qt.QLabel('Hello Qt!')
    # label.show()
    player = Player(sys.argv[1:])
    player.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
