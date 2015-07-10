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

    def __init__(self):
        super(Controllers, self).__init__()

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
        layout.setContentsMargins(0, 0, 0, 0)
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
            self.playButton.setIcon(Qt.QStyle.SP_MediaPlay)
        elif state == QMediaPlayer.PlayingState:
            self.stopButton.setEnabled(True)
            self.playButton.setIcon(Qt.QStyle.SP_MediaPause)
        elif state == QMediaPlayer.PausedState:
            self.stopButton.setEnabled(True)
            self.playButton.setIcon(Qt.QStyle.SP_MediaPlay)


class VideoWidget(Qt.QVideoWidget):
    pass


class Playlist(QtCore.QAbstractItemModel):
    def __init__(self):
        super(Playlist, self).__init__()

    def setPlaylist(self, playlist):
        pass


class HistogramWidget(Qt.QWidget):
    def __init__(self):
        super(HistogramWidget, self).__init__()

    def processFrame(self, frame):
        pass


class Player(Qt.QWidget):
    """docstring for Player"""
    fullScreenChanged = Qt.pyqtSignal(bool)

    def __init__(self, playlist):
        # create player
        super(Player, self).__init__()

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
        self.playlist.currentIndexChanged.connect(self.playistPositionChanged)

        self.player.mediaStatusChanged.connect(self.statusChanged)
        self.player.bufferStatusChanged.connect(self.bufferingProgress)
        # self.player.videoAvailableChanged.connect(self.videoAvailableChanged)
        self.player.error.connect(self.displayErrorMessage)

        # connect with VideoWidget
        self.videoWidget = VideoWidget()
        self.player.setVideoOutput(self.videoWidget)

        # connect with PlaylistModel
        self.playlistModel = Playlist()
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
        controls.stop.connect(self.videoWidget.update)

        self.player.stateChanged.connect(controls.setState)
        self.player.volumeChanged.connect(controls.setVolume)
        self.player.mutedChanged.connect(controls.setMuted)

        # create fullScreenButton
        self.fullScreenButton = Qt.QPushButton('FullScreen')
        self.fullScreenButton.setCheckable(True)

        # displayLayout
        displayLayout = Qt.QHBoxLayout()
        displayLayout.addWidget(self.videoWidget, 2)
        displayLayout.addWidget(self.playlistView)

        # controlLayout
        controlLayout = Qt.QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        # connetct controlLayout with controls
        controlLayout.addWidget(controls)
        controlLayout.addStretch(1)
        # connetct controlLayout with fullScreenButton
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

        self.setLayout(layout)

        if not self.player.isAvailable():
            Qt.QMessageBox(self, 'Unavailable service')
            # self.displayErrorMessage()
            controls.setEnabled(False)
            self.playlistView.setEnabled(False)
            self.fullScreenButton.setEnabled(False)

        self.metaDataChanged()

        self.addToPlaylist(playlist)

    def durationChanged(self):
        pass

    def positionChanged(self):
        pass

    def metaDataChanged(self):
        pass

    def playistPositionChanged(self):
        pass

    def statusChanged(self):
        pass

    def bufferingProgress(self):
        pass

    def displayErrorMessage(self):
        pass

    def jump(self):
        pass

    def seek(self):
        pass

    def previousAction(self):
        pass

    def addToPlaylist(self, playlist):
        pass

    def close(self):
        choice = Qt.QMessageBox.question(
            self,
            'Exit',
            'Exit the app?',
            Qt.QMessageBox.Yes | Qt.QMessageBox.No)

        if choice == Qt.QMessageBox.Yes:
            sys.exit()

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
