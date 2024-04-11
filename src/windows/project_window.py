from functools import partial

from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QPushButton
from PyQt5 import QtCore, QtWidgets

from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType

from resources.py.ProjectForm import Ui_ProjectForm


class ProjectWindow(BaseWindow):
    def __init__(self, project, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_ProjectForm()
        self.ui.setupUi(self.central_widget)
        self.set_scroll_area(self.ui.scrollArea)

        self.project = project

        self.ui.project_name_label.setText(self.project.name)

        self.ui.back_button.clicked.connect(self.close_project)

        self.ui.new_well_button.clicked.connect(self.goto_new_well)

        wells_buttons_list = []

        wells = self.get_database_manager().get_all_wells()
        for well in wells:
            well_button = QPushButton(well.name)
            self.ui.wells_buttons_verticalLayout.layout().addWidget(well_button)
            wells_buttons_list.append(well_button)
            well_button.clicked.connect(partial(self.goto_well, well))

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui.wells_buttons_verticalLayout.addItem(spacer)

        # Focus
        self.install_focusable_elements(
            self.ui.back_button,
            self.ui.new_well_button,
            *wells_buttons_list)

        self.start_focus = self.ui.new_well_button

    def close_project(self):
        self.app.close_database_connection()
        self.goto_start()

    def goto_start(self):
        self.switch_interface(WindowType.START_WINDOW)

    def goto_new_well(self):
        self.switch_interface(WindowType.NEW_WELL_WINDOW, self.project)

    def goto_well(self, well):
        self.switch_interface(WindowType.WELL_WINDOW, self.project, well)
