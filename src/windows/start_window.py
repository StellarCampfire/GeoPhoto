import logging
from PyQt5.QtWidgets import QFileDialog

from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType

from resources.py.StartForm import Ui_StartForm



class   StartWindow(BaseWindow):
    def __init__(self, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_StartForm()
        self.ui.setupUi(self.central_widget)

        self.ui.new_project_button.clicked.connect(self.goto_new_project)
        self.ui.open_project_button.clicked.connect(self.openProjectDialog)
        self.ui.settings_button.clicked.connect(self.goto_settings)

        # Focus
        self.install_focusable_elements(
            self.ui.new_project_button,
            self.ui.open_project_button,
            self.ui.settings_button)

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
                self.app.save_current_project_path(project)
                self.goto_project(project)

    def goto_new_project(self):
        self.switch_interface(WindowType.NEW_PROJECT_WINDOW)

    def goto_settings(self):
        self.switch_interface(WindowType.SETTINGS_WINDOW)

    def goto_project(self, project):
        self.switch_interface(WindowType.PROJECT_WINDOW, project)