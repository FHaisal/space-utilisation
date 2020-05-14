# pyinstaller Space\ Utilisation.py --add-data "icons;icons" --add-data "model;model" --add-data "tracking;tracking" --add-data "utility;utility" --add-data "people_counter.py;." --add-binary "C:\Users\faisa\AppData\Local\Programs\Python\Python37\Lib\site-packages\cv2\opencv_videoio_ffmpeg420_64.dll;cv2" --noconfirm

import sys
from PySide2 import QtCore, QtWidgets, QtGui
from people_counter import PeopleCounter


class SpaceUtilisation(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Space Utilisation')
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        app_icon = QtGui.QIcon()
        app_icon.addFile('icons/og_pc_16.png', QtCore.QSize(16, 16))
        app_icon.addFile('icons/og_pc_24.png', QtCore.QSize(24, 24))
        app_icon.addFile('icons/og_pc_32.png', QtCore.QSize(32, 32))
        app_icon.addFile('icons/og_pc_48.png', QtCore.QSize(48, 48))
        app_icon.addFile('icons/og_pc_256.png', QtCore.QSize(256, 256))
        self.setWindowIcon(app_icon)

        self.layout.addWidget(Home())

        self.setFixedSize(500, 500)
        self.show()


class Home(QtWidgets.QGroupBox):
    def __init__(self):
        super(Home, self).__init__()

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.button_style = "QPushButton { font-size: 48px; qproperty-iconSize: 48px; }"

        self.upload_video = QtWidgets.QPushButton(" Upload Video File")
        self.upload_video.setStyleSheet(self.button_style)

        self.video_source = QtWidgets.QPushButton(" Video Source")
        self.video_source.setStyleSheet(self.button_style)

        self.upload_video.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Expanding)

        self.video_source.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Expanding)

        file_icon = QtGui.QPixmap("icons/video_file.svg")
        self.upload_video.setIcon(QtGui.QIcon(file_icon))

        src_icon = QtGui.QPixmap("icons/video_src.svg")
        self.video_source.setIcon(QtGui.QIcon(src_icon))

        self.layout.addWidget(self.upload_video)
        self.layout.addWidget(self.video_source)

        self.upload_video.clicked.connect(self.run_video_stream)
        self.video_source.clicked.connect(self.run_video_source)

    def file_dialog(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "", "Video Files (*.mp4 *.avi *.mp3)")
        return fileName[0]

    def run_video_stream(self):
        path = self.file_dialog()
        if path:
            people_counter = PeopleCounter(video_url=path)
            people_counter.start()
            people_counter.stop()

    def run_video_source(self):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Information")
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setText("To stop the video stream press keyboard key: 'Q' on the video window"
                        "\nStream will begin once this dialog is closed")
        msg_box.exec()

        try:
            people_counter = PeopleCounter("http://raspberrypi:8080/?action=stream", raspi=True)
            people_counter.start()
        except:
            msg_box.setWindowTitle("Error")
            msg_box.setIcon(QtWidgets.QMessageBox.Error)
            msg_box.setText("The Raspberry Pi may not be connected, please try again!")
            msg_box.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    screen = app.primaryScreen()

    widget = SpaceUtilisation()
    width = screen.size().width() - widget.size().width()
    height = screen.size().height() - widget.size().height()
    widget.move((screen.size().width() - widget.size().width()) / 2,
                (screen.size().height() - widget.size().height()) / 2)

    sys.exit(app.exec_())
