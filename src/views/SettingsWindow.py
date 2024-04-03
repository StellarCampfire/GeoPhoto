from src.views.BaseWindow import BaseWindow
from src.views.StartWindow import StartWindow
from src.models import Project, Well, IntervalSettings

from resources.py.SattingsForm import Ui_SettingsForm


class SettingsWindow(BaseWindow):
    def __init__(self, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.ui = Ui_SettingsForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.sutter_speed_spinBox.setMinimum(int(self.get_config().get('camera', 'exposition_min', fallback='37')))
        self.ui.sutter_speed_spinBox.setMaximum(
            int(self.get_config().get('camera', 'exposition_max', fallback='300000')))
        self.ui.sutter_speed_spinBox.setValue(int(self.get_config().get('camera', 'exposition', fallback='50000')))

        self.ui.iso_spinBox.setMinimum(int(self.get_config().get('camera', 'iso_min', fallback='0')))
        self.ui.iso_spinBox.setMaximum(int(self.get_config().get('camera', 'iso_max', fallback='10000')))
        self.ui.iso_spinBox.setValue(int(self.get_config().get('camera', 'iso', fallback='100')))

        self.ui.back_pushButton.clicked.connect(lambda: self.switch_interface(StartWindow))
        self.ui.take_photo_camera.clicked.connect(self.set_controls_and_show_photo)

        self.install_focusable_elements(
            self.ui.sutter_speed_spinBox,
            self.ui.iso_spinBox,
        )

    def set_controls_and_show_photo(self):
        photo_path = self.get_photo_manager().set_controls_and_take_photo(
            Project('test_project', './'),
            Well(0, 'test_well'), IntervalSettings(),
            self.ui.sutter_speed_spinBox.value(),
            self.ui.iso_spinBox.value())
        self.switch_interface(SettingsPreviewPhoto, photo_path)
