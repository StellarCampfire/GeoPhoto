from src.views.BaseWindow import BaseWindow
from src.views.ProjectWindow import ProjectWindow
from src.views.WellWindow import WellWindow
from resources.py.NewWellForm import Ui_NewWellForm

class NewWellWindow(BaseWindow):
    def __init__(self, project, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_NewWellForm()
        self.ui.setupUi(self.centralwidget)
        self.project = project

        self.ui.project_name_input.setText(project.name)

        self.ui.back_button.clicked.connect(lambda: self.switch_interface(ProjectWindow, self.project))
        self.ui.create_new_well.clicked.connect(lambda: self.onCreateNewWellClicked())

    def onCreateNewWellClicked(self):
        well_name = self.ui.well_name_input.text()
        if well_name:
            self.create_new_well(well_name)
        else:
            self.ui.error_message_label.setText("Название скважины не может быть пустое.")

    def create_new_well(self, well_name):
        new_well_id = self.get_database_manager().add_well(well_name)
        new_well = self.get_database_manager().get_well(new_well_id)
        self.switch_interface(WellWindow, self.project, new_well)