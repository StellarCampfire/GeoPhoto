from src.views.BaseWindow import BaseWindow
from src.views.NewIntervalWindow import NewIntervalWindow
from src.views.ProjectWindow import ProjectWindow
from src.views.IntervalWindow import IntervalWindow
from resources.py.WellForm import Ui_WellForm

from src.models import IntervalSettings

from PyQt5.QtWidgets import (QSpacerItem, QSizePolicy)
from PyQt5.QtWidgets import QPushButton

INTERVAL_STEP = 0.5


class WellWindow(BaseWindow):
    def __init__(self, project, well, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_WellForm()
        self.ui.setupUi(self.centralwidget)

        self.project = project
        self.well = well

        self.ui.project_name_input.setText(project.name)
        self.ui.well_name_input.setText(self.well.name)

        self.ui.new_interval_button.clicked.connect(lambda: self.switch_interface(
            NewIntervalWindow,
            self.project,
            self.well,
            IntervalSettings(
                float(intervals[-1].interval_to),
                float(intervals[-1].interval_to) + INTERVAL_STEP,
                intervals[-1].is_marked,
                intervals[-1].condition) if intervals else IntervalSettings()
        ))

        self.ui.back_button.clicked.connect(lambda: self.switch_interface(ProjectWindow, self.project))

        self.focusable_elements.append(self.ui.back_button)

        intervals = self.get_database_manager().get_all_intervals_by_well_id(self.well.id)
        for interval in intervals:
            interval_button = QPushButton(interval.get_full_name())
            self.ui.intervals_buttons_verticalLayout.layout().addWidget(interval_button)
            self.focusable_elements.append(interval_button)
            interval_button.clicked.connect(lambda _, i=interval: self.switch_interface(
                IntervalWindow,
                self.project,
                self.well,
                i))

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui.intervals_buttons_verticalLayout.addItem(spacer)

        self.start_focus = self.ui.back_button
