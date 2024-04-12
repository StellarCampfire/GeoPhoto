import shutil
import os
import logging

from resources.py.DeleteForm import Ui_DeleteForm

from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType


class DeleteWellWindow(BaseWindow):
    def __init__(self, project, well, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.project = project
        self.well = well

        self.ui = Ui_DeleteForm()
        self.ui.setupUi(self.central_widget)

        self.ui.question_label.setText(f"Удалить скважину {self.well.name} и все содержащиеся в ней интервалы?")

        self.ui.yes_pushButton.clicked.connect(self.on_yes_clicked)
        self.ui.no_pushButton.clicked.connect(self.goto_well)

        # Focus
        self.install_focusable_elements(
            self.ui.yes_pushButton,
            self.ui.no_pushButton)

        self.start_focus = self.ui.no_pushButton

    def on_yes_clicked(self):
        self.get_database_manager().delete_well_and_related_data(self.well.id)
        path_to_delete = os.path.join(self.project.media_path, self.well.name)
        try:
            shutil.rmtree(path_to_delete)
            logging.info(f"Directory '{path_to_delete}' and all its contents have been successfully deleted.")
        except Exception as e:
            logging.error(f"Error deleting directory '{path_to_delete}': {e}")
        self.goto_project()

    def goto_well(self):
        self.switch_interface(WindowType.WELL_WINDOW, self.project, self.well)

    def goto_project(self):
        self.switch_interface(WindowType.PROJECT_WINDOW, self.project)
