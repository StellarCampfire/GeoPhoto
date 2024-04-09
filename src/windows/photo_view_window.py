from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType

from resources.py.PhotoViewForm import Ui_PhotoViewForm


class PhotoViewWindow(BaseWindow):
    def __init__(self, project, well, interval, photo, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.project = project
        self.well = well
        self.interval = interval
        self.photo = photo

        self.ui = Ui_PhotoViewForm()
        self.ui.setupUi(self.central_widget)

        self.ui.back_pushButton.clicked.connect(self.goto_interval)

        # Focus
        self.install_focusable_elements(
            self.ui.back_pushButton)

    def load_image(self):
        pixmap = QPixmap(self.photo.path)
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

    def goto_interval(self):
        self.switch_interface(WindowType.INTERVAL_WINDOW, self.project, self.well, self.interval)
