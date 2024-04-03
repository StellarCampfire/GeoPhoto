import logging

from src.views.BaseWindow import BaseWindow
from src.views.NewProjectWindow import NewProjectWindow
from src.views.SettingsWindow import SettingsWindow
from src.views.ProjectWindow import ProjectWindow

from resources.py.StartForm import Ui_StartForm

from PyQt5.QtWidgets import (QFileDialog)


class StartWindow(BaseWindow):
    def __init__(self, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_StartForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.new_project_button.clicked.connect(lambda: self.switch_interface(NewProjectWindow))
        self.ui.open_project_button.clicked.connect(self.openProjectDialog)
        self.ui.settings_button.clicked.connect(lambda: self.switch_interface(SettingsWindow))

        # Focus
        self.focusable_elements.extend([
            self.ui.new_project_button,
            self.ui.open_project_button,
            self.ui.settings_button])

        self.start_focus = self.ui.open_project_button

    def openProjectDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        project_file_path, _ = QFileDialog.getOpenFileName(self,
                                                           "Открыть файл проекта",
                                                           "",
                                                           "JSON Files (*.json)",
                                                           options=options)
        if project_file_path:
            logging.info(f"Project file selected: {project_file_path}")
            project = self.app.load_project_from_file(project_file_path)
            if project is not None:
                self.app.init_database_connection(project)
                self.switch_interface(ProjectWindow, project)
