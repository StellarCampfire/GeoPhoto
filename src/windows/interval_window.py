from functools import partial
from PyQt5.QtWidgets import QPushButton
from resources.py.IntervalForm import Ui_IntervalForm
from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType
from src.models.interval import BaseIntervalSettings


class IntervalWindow(BaseWindow):
    def __init__(self, project, well, interval, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.project = project
        self.well = well
        self.interval = interval

        self.ui = Ui_IntervalForm()
        self.ui.setupUi(self.central_widget)
        self.set_scroll_area(self.ui.scrollArea)

        self.ui.project_name_label.setText(self.project.name)
        self.ui.well_name_label.setText(self.well.name)
        self.ui.interval_name_label.setText(self.interval.get_full_name())

        self.ui.back_button.clicked.connect(self.goto_well)

        self.ui.next_interval_pushButton.clicked.connect(self.goto_new_interval)
        self.ui.delete_interval_pushButton.clicked.connect(self.goto_delete_interval)

        photos_buttons_list = []

        photos = self.get_database_manager().get_all_photos_by_interval_id(self.interval.id)
        for photo in photos:
            photo_button = QPushButton(photo.name)
            self.ui.photos_buttons_verticalLayout.layout().addWidget(photo_button)
            photos_buttons_list.append(photo_button)
            photo_button.clicked.connect(partial(self.goto_photo_view, photo))
            self.focusable_elements.append(photo_button)

        # Focus
        self.install_focusable_elements(
            self.ui.back_button,
            *photos_buttons_list,
            self.ui.next_interval_pushButton,
            self.ui.delete_interval_pushButton)

        self.start_focus = self.ui.next_interval_pushButton

    def goto_well(self):
        self.switch_interface(WindowType.WELL_WINDOW, self.project, self.well)

    def goto_new_interval(self):
        self.switch_interface(
            WindowType.NEW_INTERVAL_WINDOW,
            self.project,
            self.well,
            BaseIntervalSettings(
                self.interval.interval_to,
                self.interval.interval_to + float(self.get_config().get('logic', 'interval_step', fallback='0.5')),
                self.interval.condition,
                self.interval.is_marked))

    def goto_photo_view(self, photo):
        self.switch_interface(WindowType.PHOTO_VIEW_WINDOW, self.project, self.well, self.interval, photo)

    def goto_delete_interval(self):
        self.switch_interface(WindowType.DELETE_INTERVAL_WINDOW, self.project, self.well, self.interval)
