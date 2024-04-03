from src.views.BaseWindow import BaseWindow
from src.views.WellWindow import WellWindow
from src.views.PhotoReviewWindow import PhotoReviewWindow

from src.models import IntervalCondition, IntervalSettings
from src.custom_elements.CustomSpinBox import CustomSpinBox

from resources.py.NewIntervalForm import Ui_NewIntervalForm


class NewIntervalWindow(BaseWindow):
    def __init__(self, project, well, interval_settings, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_NewIntervalForm()
        self.ui.setupUi(self.centralwidget)

        self.project = project
        self.well = well
        self.interval_settings = interval_settings

        self.ui.project_name_label.setText(self.project.name)
        self.ui.well_name_label.setText(self.well.name)

        self.ui.back_button.clicked.connect(
            lambda: self.switch_interface(WellWindow, self.project, self.well))

        self.custom_interval_from = CustomSpinBox(
            self.ui.interval_from_doubleSpinBox,
            self.ui.interval_from_decrease_button,
            self.ui.interval_from_increase_button)

        self.custom_interval_to = CustomSpinBox(
            self.ui.interval_to_doubleSpinBox,
            self.ui.interval_to_decrease_button,
            self.ui.interval_to_increase_button
        )

        self.custom_interval_from.setSingleStep(0.05)
        self.custom_interval_to.setSingleStep(0.05)

        self.custom_interval_from.setValue(self.interval_settings.interval_from)
        self.custom_interval_to.setValue(self.interval_settings.interval_to)

        self.ui.is_marked_checkBox.setChecked(self.interval_settings.is_marked)
        if self.interval_settings.condition == IntervalCondition.WET:
            self.ui.wet_radioButton.setChecked(True)
        else:
            self.ui.dry_radioButton.setChecked(True)

        self.ui.create_new_interval_button.clicked.connect(self.onCreateNewIntervalClicked)

        self.focusable_elements.append(self.ui.back_button)
        self.focusable_elements.append(self.ui.interval_from_doubleSpinBox)
        self.focusable_elements.append(self.ui.interval_to_doubleSpinBox)
        self.focusable_elements.append(self.ui.is_marked_checkBox)
        self.focusable_elements.append(self.ui.wet_radioButton)
        self.focusable_elements.append(self.ui.dry_radioButton)
        self.focusable_elements.append(self.ui.create_new_interval_button)

        self.install_focus_event_filters()
        self.start_focus = self.ui.back_button

    def onCreateNewIntervalClicked(self):
        interval_from = self.ui.interval_from_doubleSpinBox.value()
        interval_to = self.ui.interval_to_doubleSpinBox.value()
        is_marked = self.ui.is_marked_checkBox.isChecked()
        condition = IntervalCondition.WET if self.ui.wet_radioButton.isChecked() else IntervalCondition.DRY
        self.make_photo(IntervalSettings(interval_from, interval_to, is_marked, condition))

    def make_photo(self, interval_settings):
        # photos = self.photo_manager.take_photos(self.project, self.well, interval_settings)
        self.switch_interface(
            PhotoReviewWindow,
            self.project,
            self.well,
            interval_settings,
            # photos
        )
