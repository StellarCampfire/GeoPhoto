from src.views.BaseWindow import BaseWindow
from src.views.StartWindow import StartWindow
from src.views.ProjectWindow import ProjectWindow
from resources.py.NewProjectForm import Ui_NewProjectForm
from PyQt5.QtWidgets import (QFileDialog)


class NewProjectWindow(BaseWindow):
    def __init__(self, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_NewProjectForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.back_button.clicked.connect(lambda: self.switch_interface(StartWindow))
        self.ui.choose_path_button.clicked.connect(self.chooseProjectPath)
        self.ui.create_new_project_button.clicked.connect(self.onCreateNewProjectClicked)

        # Focus
        self.focusable_elements.append(self.ui.back_button)
        self.focusable_elements.append(self.ui.project_name_input)
        self.focusable_elements.append(self.ui.choose_path_button)
        self.focusable_elements.append(self.ui.create_new_project_button)

        self.start_focus = self.ui.back_button

    def chooseProjectPath(self):
        project_dir = QFileDialog.getExistingDirectory(self, "Выберите папку для нового проекта")
        if project_dir:
            self.ui.project_path_input.setText(project_dir)

    def onCreateNewProjectClicked(self):
        project_name = self.ui.project_name_input.text()
        project_path = self.ui.project_path_input.text()
        if project_name and project_path:
            project = self.app.create_and_verify_project(project_name, project_path)
            if project is not None:
                self.switch_interface(ProjectWindow, project)
        else:
            self.ui.error_message_label.setText("Название проекта и путь не могут быть пустыми.")
