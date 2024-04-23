from src.core.window_types import WindowType
from src.windows.base_window import BaseWindow
from src.custom_elements.custom_spin_box import CustomSpinBox

from resources.py.SettingsForm import Ui_SettingsForm


class SettingsWindow(BaseWindow):
    def __init__(self, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.ui = Ui_SettingsForm()
        self.ui.setupUi(self.central_widget)
        self.set_scroll_area(self.ui.scrollArea)

        self.left_crop_spin_box = CustomSpinBox(
            self.ui.left_crop_spinBox,
            self.ui.left_crop_decrease_pushButton,
            self.ui.left_crop_increase_pushButton)
        self.left_crop_spin_box.spin_box.setValue(int(self.get_config().get("crop", "left", fallback="0")))

        self.right_crop_spin_box = CustomSpinBox(
            self.ui.right_crop_spinBox,
            self.ui.right_crop_decrease_pushButton,
            self.ui.right_crop_increase_pushButton)
        self.right_crop_spin_box.spin_box.setValue(int(self.get_config().get("crop", "right", fallback="0")))

        self.top_crop_spin_box = CustomSpinBox(
            self.ui.top_crop_spinBox,
            self.ui.top_crop_decrease_pushButton,
            self.ui.top_crop_increase_pushButton)
        self.top_crop_spin_box.spin_box.setValue(int(self.get_config().get("crop", "top", fallback="0")))

        self.bottom_crop_spin_box = CustomSpinBox(
            self.ui.bottom_crop_spinBox,
            self.ui.bottom_crop_decrease_pushButton,
            self.ui.bottom_crop_increase_pushButton)
        self.bottom_crop_spin_box.spin_box.setValue(int(self.get_config().get("crop", "bottom", fallback="0")))

        self.width_spinbox = CustomSpinBox(
            self.ui.width_spinBox,
            self.ui.width_decrease_pushButton,
            self.ui.width_increase_pushButton)
        self.width_spinbox.spin_box.setValue(int(self.get_config().get("camera", "width", fallback="0")))

        self.height_spinbox = CustomSpinBox(
            self.ui.height_spinBox,
            self.ui.height_decrease_pushButton,
            self.ui.height_increase_pushButton)
        self.height_spinbox.spin_box.setValue(int(self.get_config().get("camera", "height", fallback="0")))

        self.ui.back_pushButton.clicked.connect(self.goto_start)
        self.ui.save_settings_pushButton.clicked.connect(self.save_settings)

        # Focus
        self.install_focusable_elements(
            self.ui.back_pushButton,
            self.ui.left_crop_spinBox,
            self.ui.right_crop_spinBox,
            self.ui.top_crop_spinBox,
            self.ui.bottom_crop_spinBox,
            self.ui.width_spinBox,
            self.ui.height_spinBox,
            self.ui.save_settings_pushButton)

        self.start_focus = self.ui.back_pushButton

    def goto_start(self):
        self.switch_interface(WindowType.START_WINDOW)

    def save_settings(self):
        self.get_config().set("crop", "left", str(self.left_crop_spin_box.value()))
        self.get_config().set("crop", "right", str(self.right_crop_spin_box.value()))
        self.get_config().set("crop", "top", str(self.top_crop_spin_box.value()))
        self.get_config().set("crop", "bottom", str(self.bottom_crop_spin_box.value()))
        self.get_config().set("camera", "width", str(self.width_spinbox.value()))
        self.get_config().set("camera", "height", str(self.height_spinbox.value()))
        self.goto_start()
