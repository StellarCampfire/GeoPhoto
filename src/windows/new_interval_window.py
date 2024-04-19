from resources.py.NewIntervalForm import Ui_NewIntervalForm
from src.core.window_types import WindowType
from src.windows.base_window import BaseWindow
from src.custom_elements.custom_spin_box import CustomSpinBox
from src.models.interval import IntervalCondition, BaseIntervalSettings


class NewIntervalWindow(BaseWindow):
    def __init__(self, project, well, interval_settings, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_NewIntervalForm()
        self.ui.setupUi(self.central_widget)

        self.project = project
        self.well = well
        self.interval_settings = interval_settings

        self.ui.project_name_label.setText(self.project.name)
        self.ui.well_name_label.setText(self.well.name)

        self.ui.back_button.clicked.connect(self.goto_well)

        self.custom_interval_from = CustomSpinBox(
            self.ui.interval_from_doubleSpinBox,
            self.ui.interval_from_decrease_button,
            self.ui.interval_from_increase_button)

        self.custom_interval_to = CustomSpinBox(
            self.ui.interval_to_doubleSpinBox,
            self.ui.interval_to_decrease_button,
            self.ui.interval_to_increase_button
        )

        self.custom_interval_from.setSingleStep(
            float(self.get_config().get("logic", "interval_button_step", fallback="0.05"))
        )
        self.custom_interval_to.setSingleStep(
            float(self.get_config().get("logic", "interval_button_step", fallback="0.05"))
        )

        self.custom_interval_from.setValue(self.interval_settings.interval_from)
        self.custom_interval_to.setValue(self.interval_settings.interval_to)

        self.ui.is_marked_checkBox.setChecked(self.interval_settings.is_marked)
        if self.interval_settings.condition == IntervalCondition.WET:
            self.ui.wet_radioButton.setChecked(True)
        else:
            self.ui.dry_radioButton.setChecked(True)

        self.ui.create_new_interval_button.clicked.connect(self.goto_photo_review)

        # Focus
        self.install_focusable_elements(
            self.ui.back_button,
            self.ui.interval_from_doubleSpinBox,
            self.ui.interval_to_doubleSpinBox,
            self.ui.is_marked_checkBox,
            self.ui.wet_radioButton,
            self.ui.dry_radioButton,
            self.ui.create_new_interval_button)

        self.start_focus = self.ui.create_new_interval_button

    def goto_well(self):
        self.switch_interface(WindowType.WELL_WINDOW, self.project, self.well)

    def goto_photo_review(self):
        self.switch_interface(
            WindowType.PHOTO_REVIEW_WINDOW,
            self.project,
            self.well,
            BaseIntervalSettings(
                self.ui.interval_from_doubleSpinBox.value(),
                self.ui.interval_to_doubleSpinBox.value(),
                IntervalCondition.WET if self.ui.wet_radioButton.isChecked() else IntervalCondition.DRY,
                self.ui.is_marked_checkBox.isChecked(),
            ))
