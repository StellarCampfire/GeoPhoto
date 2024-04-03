from src.views.BaseWindow import BaseWindow
from src.views.SettingsWindow import SettingsWindow
from resources.py.PhotoViewForm import Ui_PhotoViewForm

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class SettingsPreviewPhoto(BaseWindow):
    def __init__(self, photo_path, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.photo_path = photo_path

        self.ui = Ui_PhotoViewForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.back_pushButton.clicked.connect(
            lambda: self.switch_interface(SettingsWindow))

    def load_image(self):
        pixmap = QPixmap(self.photo_path)
        scaled_pixmap = pixmap.scaled(self.ui.photo_label.size(), Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation)
        self.ui.photo_label.setPixmap(scaled_pixmap)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'ui'):
            self.load_image()