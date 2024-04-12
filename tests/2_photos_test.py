import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from picamera2 import Picamera2

class CameraThread(QThread):
    photoTaken = pyqtSignal(str, name='photoTaken')

    def __init__(self, camera_index, photo_path):
        super().__init__()
        self.camera_index = camera_index
        self.photo_path = photo_path

    def run(self):
        try:
            camera = Picamera2(self.camera_index)
            config = camera.create_still_configuration()
            camera.configure(config)
            camera.start()
            camera.capture_file(self.photo_path)
        except Exception as e:
            print(f"Error capturing photo with camera {self.camera_index}: {e}")
        finally:
            if camera:
                camera.stop()
                camera.close()  # Explicitly close the camera to free up resources
            self.photoTaken.emit(self.photo_path)

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Control App")
        self.setGeometry(100, 100, 800, 600)
        self.photoLabel = QLabel(self)
        self.photoLabel.setFixedSize(640, 480)
        self.setup_buttons()

    def setup_buttons(self):
        self.takePhotoButton = QPushButton("Take Photos Sequentially", self)
        self.exitButton = QPushButton("Exit", self)
        layout = QVBoxLayout()
        layout.addWidget(self.photoLabel)
        layout.addWidget(self.takePhotoButton)
        layout.addWidget(self.exitButton)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.takePhotoButton.clicked.connect(self.take_sequential_photos)
        self.exitButton.clicked.connect(self.close)

    def take_sequential_photos(self):
        self.take_photo(0)

    def take_photo(self, camera_index):
        photo_path = f"photo_{camera_index + 1}.jpg"
        thread = CameraThread(camera_index, photo_path)
        thread.photoTaken.connect(self.display_photo)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self.on_photo_thread_finished)  # Connect finish event to handler

        thread.start()

    def on_photo_thread_finished(self):
        sender = self.sender()  # Get the thread that sent the signal
        if sender.camera_index == 0:
            self.take_photo(1)  # Start second camera after first has finished

    def display_photo(self, path):
        pixmap = QPixmap(path)
        self.photoLabel.setPixmap(pixmap.scaled(self.photoLabel.size(), aspectRatioMode=1))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
