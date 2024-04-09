from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType

from resources.py.NewWellForm import Ui_NewWellForm


class NewWellWindow(BaseWindow):
    def __init__(self, project, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_NewWellForm()
        self.ui.setupUi(self.central_widget)
        self.project = project

        self.ui.project_name_label.setText(project.name)

        self.ui.back_button.clicked.connect(self.goto_project)
        self.ui.create_new_well.clicked.connect(self.on_create_new_well_clicked)

        # Focus
        self.install_focusable_elements(
            self.ui.back_button,
            self.ui.well_name_input,
            self.ui.create_new_well
        )

        self.start_focus = self.ui.well_name_input

    def on_create_new_well_clicked(self):
        well_name = self.ui.well_name_input.text()
        if well_name:
            new_well_id = self.get_database_manager().add_well(well_name)
            new_well = self.get_database_manager().get_well(new_well_id)
            self.goto_well(new_well)
        else:
            self.ui.error_message_label.setText("Название скважины не может быть пустое.")

    def goto_project(self):
        self.switch_interface(WindowType.PROJECT_WINDOW, self.project)

    def goto_well(self, well):
        self.switch_interface(WindowType.WELL_WINDOW, self.project, well)
