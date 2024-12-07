from PyQt5 import QtWidgets, QtGui, QtCore
import vlc
import platform
import os
import sys

class MediaPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Player")
        self.instance = vlc.Instance()
        self.media = None
        self.mediaplayer = self.instance.media_player_new()
        self.is_paused = False
        self.create_ui()

    def create_ui(self):
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        if platform.system() == "Darwin":
            self.videoframe = QtWidgets.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtWidgets.QFrame()

        self.videoframe.setAutoFillBackground(True)
        self.setup_ui_elements()
        self.setup_menus()

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

    def setup_ui_elements(self):
        palette = self.videoframe.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(palette)

        self.positionslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)

        self.hbuttonbox = QtWidgets.QHBoxLayout()
        self.playbutton = QtWidgets.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.play_pause)

        self.stopbutton = QtWidgets.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.stop)

        self.volumeslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.volumeslider.valueChanged.connect(self.set_volume)
        self.hbuttonbox.addWidget(self.volumeslider)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

    def setup_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        
        open_action = QtWidgets.QAction("Open Video", self)
        close_action = QtWidgets.QAction("Exit", self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)

        open_action.triggered.connect(self.open_file)
        close_action.triggered.connect(sys.exit)

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.is_paused = True
            self.timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            self.playbutton.setText("Pause")
            self.timer.start()
            self.is_paused = False

    def stop(self):
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def open_file(self):
        dialog_txt = "Select Video File"
        filename = QtWidgets.QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename[0]:
            return

        self.media = self.instance.media_new(filename[0])
        self.mediaplayer.set_media(self.media)
        self.media.parse()
        self.setWindowTitle(self.media.get_meta(0))

        if platform.system() == "Linux":
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows":
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin":
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        self.play_pause()

    def set_volume(self, volume):
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self):
        self.timer.stop()
        pos = self.positionslider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        self.timer.start()

    def update_ui(self):
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.positionslider.setValue(media_pos)

        if not self.mediaplayer.is_playing():
            self.timer.stop()
            if not self.is_paused:
                self.stop()

def main():
    app = QtWidgets.QApplication(sys.argv)
    player = MediaPlayer()
    player.show()
    player.resize(640, 480)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
