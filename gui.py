__author__ = 'Jake Lowey'

import sys
import vlc
from PyQt4 import QtGui, QtCore
from databaseInteraction import *


class Player(QtGui.QMainWindow):
    """A simple Media Player using VLC and Qt
    """
    def __init__(self, master=None):
        super(Player,self).__init__()
        self.setWindowTitle("Media Player")

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        # self.db = DataBase()

        self.createUI()
        self.isPaused = False

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin": # for MacOS
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtGui.QFrame()
        self.palette = self.videoframe.palette()
        self.palette.setColor (QtGui.QPalette.Window,
                               QtGui.QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.connect(self.positionslider, QtCore.SIGNAL("sliderMoved(int)"), self.setPosition)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.stopbutton = QtGui.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                     self.Stop)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.connect(self.volumeslider, QtCore.SIGNAL("valueChanged(int)"), self.setVolume)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

        open = QtGui.QAction("&Open", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)
        exit = QtGui.QAction("&Exit", self)
        self.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        filemenu.addAction(exit)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.updateUI)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))
        if not filename:
            return

        # create the media
        if sys.version < '3':
            filename = unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())
        self.PlayPause()

    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)

        if not self.mediaplayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()


class display(QtGui.QWidget):

    def __init__(self, master=None):
        super(display, self).__init__()
        # self.setWindowTitle("Media Player")
        self.initUI()

    def initUI(self):
        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        movies = []
        for root, dirs, files in os.walk("D:\\"):
            for f in files:
                if f.endswith(vlc_formats):
                    print(f)
                    guess = guessit.guess_movie_info(f, info=["filename"])
                    movies.append([guess["title"], os.path.join(root,f)])

        mysize = self.geometry()

        numAcross = max(int(mysize.width()/240),1)
        # numHeight = int(mysize.height()/120)
        # print(str(numAcross) + " " + str(numHeight) + " \n")
        positions = []
        for i in range(int(len(movies)/numAcross) + 2):
            for j in range(numAcross):
                positions.append((i,j))

        self.lbl = QtGui.QLabel(self)
        self.lbl.setText("hey there")
        grid.addWidget(self.lbl, *(positions[-1]))
        for q in range(len(movies)):
            if (q < len(movies)):
                button = QtGui.QPushButton(movies[(positions[q][0]*(numAcross) + positions[q][1])][0])
                button.clicked.connect(self.buttonClicked)
                button.path = movies[(positions[q][0]*(numAcross) + positions[q][1])][1]
                # button.emit(QtCore.SIGNAL(movies[(positions[q][0]*(numAcross) + positions[q][1])][0]), movies[(positions[q][0]*(numAcross) + positions[q][1])][1])
                grid.addWidget(button,*(positions[q]))

        # self.widget.move(300, 150)

        self.show()


    def buttonClicked(self):
        sender = self.sender()
        self.lbl.setText(sender.path)
        # player = Player()



class mainGUI(QtGui.QMainWindow):

    def __init__(self, master=None):
        self.mWindow = QtGui.QMainWindow.__init__(self, master)
        self.wid = QtGui.QWidget()
        self.buildUI()

    def buildUI(self):
        self.setWindowIcon(QtGui.QIcon('Ap_icon.png'))
        self.buttons = display(self.wid)
        # self.player = Player(self.mWindow)
        # self.player.resize(640,480)