from src.core.window_types import WindowType
from src.windows.base_window import BaseWindow
from src.custom_elements.custom_spin_box import CustomSpinBox

from resources.py.SettingsForm import Ui_SettingsForm


class SettingsWindow(BaseWindow):
    def __init__(self, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.ui = Ui_SettingsForm()
        self.ui.setupUi(self.central_widget)

        self.exp_spin_box = CustomSpinBox(
            self.ui.exp_spinBox,
            self.ui.exp_decrease_pushButton,
            self.ui.exp_increase_pushButton)

        self.exp_spin_box.spin_box.setMinimum(int(self.get_config().get('camera', 'exposition_min', fallback='-8')))
        self.exp_spin_box.spin_box.setMaximum(
            int(self.get_config().get('camera', 'exposition_max', fallback='8')))
        self.exp_spin_box.spin_box.setValue(int(self.get_config().get('camera', 'exposition', fallback='0')))
        self.exp_spin_box.setSingleStep(1)

        self.iso_spin_box = CustomSpinBox(
            self.ui.iso_spinBox,
            self.ui.iso_decrease_pushButton,
            self.ui.iso_increase_pushButton)

        self.iso_spin_box.spin_box.setMinimum(int(self.get_config().get('camera', 'iso_min', fallback='0')))
        self.iso_spin_box.spin_box.setMaximum(int(self.get_config().get('camera', 'iso_max', fallback='10000')))
        self.iso_spin_box.spin_box.setValue(int(self.get_config().get('camera', 'iso', fallback='100')))

        self.ui.back_pushButton.clicked.connect(self.goto_start)

        self.ui.take_photo_camera_1.clicked.connect(lambda: self.set_controls_and_show_photo(1))
        self.ui.take_photo_camera_2.clicked.connect(lambda: self.set_controls_and_show_photo(2))

        # Focus
        self.install_focusable_elements(
            self.ui.back_pushButton,
            self.ui.exp_spinBox,
            self.ui.iso_spinBox,
            self.ui.take_photo_camera_1,
            self.ui.take_photo_camera_2)

        self.get_photo_manager().get_default_still_config()

    def goto_start(self):
        self.switch_interface(WindowType.SETTINGS_WINDOW)
