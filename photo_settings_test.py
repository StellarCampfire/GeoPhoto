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
from main import IntervalSettings


from resources.py.camera_settings_test import Ui_MainWindow


DATA_FOLDER_PATH = os.path.join("~", ".geo_photo")
INTERVAL_STEP = 0.5
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='geo_photo_app.log')

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.sutter_speed_spinBox.setMinimum(37)
        self.ui.sutter_speed_spinBox.setMaximum(30000)
        self.ui.sutter_speed_spinBox.setValue(1000)

        self.ui.take_photo_camera_1.clicked.connect(lambda : ph_manager.take_photo_with_first_camera(
            {'name': 'someproject'},
            {'name': 'well'},
            IntervalSettings()))



if __name__ == '__main__':
    sys.excepthook = handle_exception

    ph_manager = None
    try:
        logging.info(f"Trying to start photo manager")
        from src.photo_module import PhotoModule

        ph_manager = PhotoModule()
        ph_manager.get_exposure_settins_value()
        logging.info(f"Photo manager stated.")
    except Exception as e:
        logging.error(f"Failed to initialize photo manager: {e}")

    if ph_manager is None:
        logging.info(f"Trying to start photo manager EMULATOR")
        from src.photo_module_emulator import PhotoModuleEmulator

        ph_manager = PhotoModuleEmulator()
        logging.info(f"Photo manager EMULATOR stated.")

    app = QApplication(sys.argv)

    window = App()
    window.showFullScreen()

    logging.info("App started")

    sys.exit(app.exec_())