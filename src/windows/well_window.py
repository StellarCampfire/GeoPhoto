from functools import partial

from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QPushButton

from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType
from src.models.interval import BaseIntervalSettings

from resources.py.WellForm import Ui_WellForm


class WellWindow(BaseWindow):
    def __init__(self, project, well, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_WellForm()
        self.ui.setupUi(self.central_widget)
        self.set_scroll_area(self.ui.scrollArea)

        self.project = project
        self.well = well

        self.ui.project_name_label.setText(project.name)
        self.ui.well_name_label.setText(self.well.name)

        self.focusable_elements.append(self.ui.back_button)

        intervals_buttons_list = []

        self.intervals = self.get_database_manager().get_all_intervals_by_well_id(self.well.id)
        for interval in self.intervals:
            interval_button = QPushButton(interval.get_full_name())
            self.ui.intervals_buttons_verticalLayout.layout().addWidget(interval_button)
            intervals_buttons_list.append(interval_button)
            interval_button.clicked.connect(partial(self.goto_interval, interval))

        self.ui.back_button.clicked.connect(self.goto_project)
        self.ui.new_interval_button.clicked.connect(self.goto_new_interval)
        self.ui.delete_well_pushButton.clicked.connect(self.goto_delete_well)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui.intervals_buttons_verticalLayout.addItem(spacer)

        # Focus
        self.install_focusable_elements(
            self.ui.back_button,
            self.ui.new_interval_button,
            *intervals_buttons_list,
            self.ui.delete_well_pushButton)

        self.start_focus = self.ui.new_interval_button

    def goto_new_interval(self):
        last_interval = self.intervals[-1] if self.intervals else None
        self.switch_interface(
            WindowType.NEW_INTERVAL_WINDOW,
            self.project,
            self.well,
            BaseIntervalSettings(
                float(last_interval.interval_to),
                float(last_interval.interval_to) + float(self.get_config()
                                                         .get('logic', 'interval_step', fallback='0.5')),
                last_interval.condition,
                last_interval.is_marked
            ) if last_interval else BaseIntervalSettings()
        )

    def goto_interval(self, interval):
        self.switch_interface(WindowType.INTERVAL_WINDOW, self.project, self.well, interval)

    def goto_project(self):
        self.switch_interface(WindowType.PROJECT_WINDOW, self.project)

    def goto_delete_well(self):
        self.switch_interface(WindowType.DELETE_WELL_WINDOW, self.project, self.well)
