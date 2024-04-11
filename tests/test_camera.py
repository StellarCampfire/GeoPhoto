import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from picamera2 import Picamera2

class CameraApp(QMainWindow):
    def __init__(self, camera_num):
        super().__init__()

        self.camera_num = camera_num

        self.setWindowTitle("Camera Control App")
        self.setGeometry(100, 100, 800, 600)

        self.photoLabel = QLabel(self)
        self.photoLabel.setFixedSize(640, 480)

        self.takePhotoCamera1Button = QPushButton("Take Photo Camera 1", self)
        self.exitButton = QPushButton("Exit", self)

        layout = QVBoxLayout()
        layout.addWidget(self.photoLabel)
        layout.addWidget(self.takePhotoCamera1Button)
        layout.addWidget(self.exitButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Инициализация камеры
        try:
            self.camera = Picamera2(self.camera_num)
            config = self.camera.create_still_configuration()
            self.camera.configure(config)
            print("Camera initialized successfully.")
        except Exception as e:
            print(f"Error initializing camera: {e}")

        # Подключение обработчиков кнопок
        self.takePhotoCamera1Button.clicked.connect(self.take_photo)
        self.exitButton.clicked.connect(self.close)

    def take_photo(self):
        print(f"Taking photo with camera {self.camera_num}...")
        photo_path = f"photo_{self.camera_num}.jpg"
        try:
            self.camera.start()
            self.camera.capture_file(photo_path)
            self.camera.stop()
            print(f"Photo taken and saved at {photo_path}")
            self.display_photo(photo_path)
        except Exception as e:
            print(f"Failed to take photo with camera {self.camera_num}: {e}")

    def display_photo(self, path):
        pixmap = QPixmap(path)
        self.photoLabel.setPixmap(pixmap.scaled(self.photoLabel.size(), aspectRatioMode=1))
        print(f"Displaying photo {path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraApp(0 if len(sys.argv) < 2 else int(sys.argv[1]))
    window.show()
    sys.exit(app.exec_())
