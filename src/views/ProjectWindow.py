from src.views.BaseWindow import BaseWindow
from src.views.NewWellWIndow import NewWellWindow
from src.views.WellWindow import WellWindow
from src.views.StartWindow import StartWindow

from PyQt5.QtWidgets import (QSpacerItem, QSizePolicy)
from PyQt5.QtWidgets import QPushButton
from resources.py.ProjectForm import Ui_ProjectForm


class ProjectWindow(BaseWindow):
    def __init__(self, project, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_ProjectForm()
        self.ui.setupUi(self.centralwidget)

        self.project = project

        self.ui.back_button.clicked.connect(lambda: self.close_project())

        self.ui.new_well_button.clicked.connect(lambda: self.switch_interface(
            NewWellWindow,
            self.project))

        self.focusable_elements.append(self.ui.back_button)
        self.focusable_elements.append(self.ui.new_well_button)

        wells = self.get_database_manager().get_all_wells()
        for well in wells:
            well_button = QPushButton(well.name)
            self.ui.wells_buttons_verticalLayout.layout().addWidget(well_button)
            self.focusable_elements.append(well_button)
            well_button.clicked.connect(
                lambda _, w=well: self.switch_interface(
                    WellWindow, self.project, w))

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui.wells_buttons_verticalLayout.addItem(spacer)

        self.start_focus = self.ui.back_button

    def close_project(self):
        self.app.close_database_connection()
        self.switch_interface(StartWindow)
