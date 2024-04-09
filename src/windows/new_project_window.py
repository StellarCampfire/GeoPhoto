from PyQt5.QtWidgets import QFileDialog
from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType

from resources.py.NewProjectForm import Ui_NewProjectForm


class NewProjectWindow(BaseWindow):
    def __init__(self, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_NewProjectForm()
        self.ui.setupUi(self.central_widget)

        self.ui.back_button.clicked.connect(self.goto_start)
        self.ui.choose_path_button.clicked.connect(self.choose_project_path)
        self.ui.create_new_project_button.clicked.connect(self.on_create_new_project_clicked)

        # Focus
        self.install_focusable_elements(
            self.ui.back_button,
            self.ui.project_name_input,
            self.ui.choose_path_button,
            self.ui.create_new_project_button)

        self.start_focus = self.ui.project_name_input

    def choose_project_path(self):
        project_dir = QFileDialog.getExistingDirectory(self, "Выберите папку для нового проекта")
        if project_dir:
            self.ui.project_path_input.setText(project_dir)

    def on_create_new_project_clicked(self):
        project_name = self.ui.project_name_input.text()
        project_path = self.ui.project_path_input.text()
        if project_name and project_path:
            project = self.app.create_and_verify_project(project_name, project_path)
            if project is not None:
                self.goto_project(project)
        else:
            self.ui.error_message_label.setText("Название проекта и путь не могут быть пустыми.")

    def goto_start(self):
        self.switch_interface(WindowType.START_WINDOW)

    def goto_project(self, project):
        self.switch_interface(WindowType.PROJECT_WINDOW, project)
