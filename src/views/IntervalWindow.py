from src.views.BaseWindow import BaseWindow
from src.views.WellWindow import WellWindow
from src.views.NewIntervalWindow import NewIntervalWindow
from src.views.PhotoViewWindow import PhotoViewWindow
from resources.py.IntervalForm import Ui_IntervalForm

from src.models import IntervalSettings

from PyQt5.QtWidgets import QPushButton

# TODO config value
INTERVAL_STEP = 0.5


class IntervalWindow(BaseWindow):
    def __init__(self, project, well, interval, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.project = project
        self.well = well
        self.interval = interval

        self.ui = Ui_IntervalForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.project_name_label.setText(self.project.name)
        self.ui.well_name_label.setText(self.well.name)

        self.ui.back_button.clicked.connect(lambda: self.switch_interface(
            WellWindow,
            self.project,
            self.well
        ))

        self.ui.next_interval_pushButton.clicked.connect(lambda: self.switch_interface(
            NewIntervalWindow,
            self.project,
            self.well,
            IntervalSettings(
                self.interval.interval_to,
                self.interval.interval_to + INTERVAL_STEP,
                self.interval.is_marked,
                self.interval.condition)))

        self.focusable_elements.append(self.ui.back_button)

        photos = self.get_database_manager().get_all_photos_by_interval_id(self.interval.id)
        for photo in photos:
            photo_button = QPushButton(photo.name)
            self.ui.photos_buttons_verticalLayout.layout().addWidget(photo_button)
            self.focusable_elements.append(photo_button)
            photo_button.clicked.connect(
                lambda _, p=photo: self.switch_interface(PhotoViewWindow, self.project, self.well, self.interval, p))
            self.focusable_elements.append(photo_button)

        self.focusable_elements.append(self.ui.next_interval_pushButton)
