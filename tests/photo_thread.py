from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from picamera2 import Picamera2
import sys

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
            camera.stop()
            camera.close()  # Explicitly close the camera
            self.photoTaken.emit(self.photo_path)
        except Exception as e:
            print(f"Error capturing photo with camera {self.camera_index}: {e}")

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Control App")
        self.setGeometry(100, 100, 800, 600)
        self.photoLabel = QLabel(self)
        self.photoLabel.setFixedSize(640, 480)
        self.setup_buttons()
        self.camera_threads = []

    def setup_buttons(self):
        self.takePhotoCamera1Button = QPushButton("Take Photo Camera 1", self)
        self.takePhotoCamera2Button = QPushButton("Take Photo Camera 2", self)
        self.exitButton = QPushButton("Exit", self)
        layout = QVBoxLayout()
        layout.addWidget(self.photoLabel)
        layout.addWidget(self.takePhotoCamera1Button)
        layout.addWidget(self.takePhotoCamera2Button)
        layout.addWidget(self.exitButton)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.takePhotoCamera1Button.clicked.connect(lambda: self.take_photo(0))
        self.takePhotoCamera2Button.clicked.connect(lambda: self.take_photo(1))
        self.exitButton.clicked.connect(self.close)

    def take_photo(self, camera_index):
        photo_path = f"photo_{camera_index + 1}.jpg"
        thread = CameraThread(camera_index, photo_path)
        thread.photoTaken.connect(self.display_photo)
        thread.finished.connect(thread.deleteLater)  # Ensure thread is cleaned up properly
        thread.start()
        self.camera_threads.append(thread)  # Keep reference to avoid garbage collection

    def display_photo(self, path):
        pixmap = QPixmap(path)
        self.photoLabel.setPixmap(pixmap.scaled(self.photoLabel.size(), Qt.KeepAspectRatio))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
