import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from picamera2 import Picamera2

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Установка размеров окна
        self.setWindowTitle("Camera Control App")
        self.setGeometry(100, 100, 800, 600)

        # Инициализация виджетов
        self.photoLabel = QLabel(self)
        self.photoLabel.setFixedSize(640, 480)

        self.takePhotoCamera1Button = QPushButton("Take Photo Camera 1", self)
        self.takePhotoCamera2Button = QPushButton("Take Photo Camera 2", self)
        self.takePhotoCameraBothButton = QPushButton("Take Photo Camera Both", self)
        self.exitButton = QPushButton("Exit", self)

        # Расположение виджетов
        layout = QVBoxLayout()
        layout.addWidget(self.photoLabel)
        layout.addWidget(self.takePhotoCamera1Button)
        layout.addWidget(self.takePhotoCamera2Button)
        layout.addWidget(self.exitButton)

        # Контейнер для виджетов
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Инициализация камер
        try:
            self.camera1 = Picamera2(0)
            self.camera2 = Picamera2(1)
            config = self.camera1.create_still_configuration()
            self.camera1.configure(config)
            self.camera2.configure(config)
        except Exception as e:
            print(f"Error initializing cameras: {e}")

        # Подключение событий
        self.takePhotoCamera1Button.clicked.connect(lambda: self.take_photo(self.camera1))
        self.takePhotoCamera2Button.clicked.connect(lambda: self.take_photo(self.camera2))
        self.takePhotoCameraBothButton.clicked.connect(lambda: self.take_photo(self.camera2))
        self.exitButton.clicked.connect(self.close)

    def take_photo(self, camera):
        photo_path = "photo.jpg"
        camera.start()
        camera.capture_file(photo_path)
        camera.stop()
        self.display_photo(photo_path)

    def takeBothPhoto(self):
        photo_path_1 = "photo_both_1.jpg"
        photo_path_2 = "photo_both_2.jpg"
        self.camera1.start()
        self.camera1.capture_file(photo_path_1)
        self.camera1.stop()
        self.camera2.start()
        self.camera2.capture_file(photo_path_2)
        self.camera2.stop()

    def display_photo(self, path):
        pixmap = QPixmap(path)
        self.photoLabel.setPixmap(pixmap.scaled(self.photoLabel.size(), aspectRatioMode=1))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
