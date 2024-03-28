import os
import sys
import logging

from PyQt5 import uic

from src.data_base_module import DBManager

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QScrollArea, QMainWindow, QLabel, QStackedWidget, QLineEdit, QDoubleSpinBox,
                             QRadioButton, QCheckBox, QFileDialog)
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QPixmap



DATA_FOLDER_PATH = os.path.join("~", ".geo_photo")
INTERVAL_STEP = 0.5
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='geo_photo_app.log')

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)


class MainWindow(QMainWindow):
    def __init__(self, database_manager, photo_manager):
        super().__init__()
        self.setWindowTitle("GeoPhoto")

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создание и добавление главного интерфейса
        # self.main_widget = ChooseProjectWidget(database_manager, photo_manager, self.switch_interface)
        # self.stacked_widget.addWidget(self.main_widget)

        # self.main_widget = StartWidget(photo_manager, self.switch_interface)
        self.stacked_widget.addWidget(self.main_widget)

    def switch_interface(self, interface_class, *args, **kwargs):
        widget = interface_class(*args, **kwargs, switch_interface_callback=self.switch_interface, parent=None)
        self.clean_stacked_widget()
        self.stacked_widget.addWidget(widget)
        self.stacked_widget.setCurrentWidget(widget)

    def clean_stacked_widget(self):
        while self.stacked_widget.count() > 0:
            widget_to_remove = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join('resources', 'ui', 'test.ui'), self)


if __name__ == '__main__':
    sys.excepthook = handle_exception

    app = QApplication(sys.argv)

    window = App()
    window.showFullScreen()

    logging.info("App started")

    sys.exit(app.exec_())