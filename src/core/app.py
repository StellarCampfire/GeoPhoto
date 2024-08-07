import json
import logging
import os
import asyncio
import sys

from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from src.core.window_types import WindowType
from src.models.project import Project

from src.utils.data_base_manager import DataBaseManager

from src.utils.photo_manager.photo_manager_emulator import PhotoManagerEmulator
from src.utils.photo_manager.photo_manager import PhotoManager, check_cameras

from src.windows.start_window import StartWindow
from src.windows.interval_window import IntervalWindow
from src.windows.new_interval_window import NewIntervalWindow
from src.windows.new_project_window import NewProjectWindow
from src.windows.new_well_window import NewWellWindow
from src.windows.photo_review_window import PhotoReviewWindow
from src.windows.photo_view_window import PhotoViewWindow
from src.windows.project_window import ProjectWindow
from src.windows.well_window import WellWindow
from src.windows.delete_well_window import DeleteWellWindow
from src.windows.delete_interval_window import DeleteIntervalWindow
from src.windows.settings_window import SettingsWindow

LAST_PROJECT_SAVE = './last_project_save.txt'

class App(QMainWindow):
    def __init__(self, sys_argv, config_manager, emulate=False, resolution=None):
        logging.debug("Initializing the application.")
        super().__init__()

        self.current_window = None
        self.resolution = resolution
        self.config_manager = config_manager
        self.db_manager = None
        self.photo_manager = None

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        logging.debug(f'Trying to start photo manager... emulate: {str(emulate)}')
        if emulate:
            self.init_photo_manager_emulator()
        else:
            self.init_photo_manager()

        logging.debug('Switching start window...')

        self.open_correct_start_window()

        logging.debug('App started.')

        if self.resolution:
            width, height = map(int, self.resolution.split('x'))
            self.setGeometry(100, 100, width, height)
        else:
            self.showFullScreen()
        self.show()

    def switch_interface(self, window_type, *args, **kwargs):
        widget = self.create_window(window_type, *args, **kwargs)
        self.clean_stacked_widget()
        self.stacked_widget.addWidget(widget)
        self.stacked_widget.setCurrentWidget(widget)

    def clean_stacked_widget(self):
        while self.stacked_widget.count() > 0:
            widget_to_remove = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

    def create_window(self, window_type, *args, **kwargs):
        logging.debug(f"Creating a new window of type {window_type}.")
        if window_type == WindowType.START_WINDOW:
            return StartWindow(self, *args, **kwargs)
        elif window_type == WindowType.SETTINGS_WINDOW:
            return SettingsWindow(self, *args, **kwargs)
        elif window_type == WindowType.NEW_PROJECT_WINDOW:
            return NewProjectWindow(self, *args, **kwargs)
        elif window_type == WindowType.PROJECT_WINDOW:
            return ProjectWindow(*args, app_instance=self, **kwargs)
        elif window_type == WindowType.NEW_WELL_WINDOW:
            return NewWellWindow(*args, app_instance=self, **kwargs)
        elif window_type == WindowType.WELL_WINDOW:
            return WellWindow(*args, app_instance=self, **kwargs)
        elif window_type == WindowType.NEW_INTERVAL_WINDOW:
            return NewIntervalWindow(*args, app_instance=self, **kwargs)
        elif window_type == WindowType.INTERVAL_WINDOW:
            return IntervalWindow(*args, app_instance=self, **kwargs)
        elif window_type == WindowType.PHOTO_REVIEW_WINDOW:
            return PhotoReviewWindow(*args, app_instance=self, **kwargs)
        elif window_type is WindowType.PHOTO_VIEW_WINDOW:
            return PhotoViewWindow(*args, app_instance=self, **kwargs)
        elif window_type == WindowType.DELETE_WELL_WINDOW:
            return DeleteWellWindow(*args, app_instance=self, **kwargs)
        elif window_type == WindowType.DELETE_INTERVAL_WINDOW:
            return DeleteIntervalWindow(*args, app_instance=self, **kwargs)
        else:
            logging.error(f"Unknown window type: {window_type}")
            raise ValueError(f"Unknown window type: {window_type}")

    def open_correct_start_window(self):
        project_path = None

        if os.path.exists(LAST_PROJECT_SAVE):
            with open(LAST_PROJECT_SAVE, 'r', encoding='utf-8') as file:
                project_path = file.read().strip()

        if project_path and os.path.exists(project_path):
            project = self.load_project_from_file(project_path)
            if project:
                self.init_database_connection(project)
                self.switch_interface(WindowType.PROJECT_WINDOW, project)
                return

        self.switch_interface(WindowType.START_WINDOW)

    def init_database_connection(self, project):
        """Initializes the database connection for the given project."""
        if not self.db_manager:
            self.db_manager = DataBaseManager(project)
            logging.info(f"Database initialized for project {project.name}.")

    def close_database_connection(self):
        """Closes the current database connection, if any."""
        if self.db_manager:
            self.db_manager.close_connection()
            self.db_manager = None
            logging.info("Database connection closed.")

    def load_project_from_file(self, file_path):
        """Loads project from a specified JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                project_data = json.load(file)
                project = Project(project_data["name"], os.path.dirname(file_path))
                self.init_database_connection(project)
                logging.info(f"Project loaded and database initialized for {project.name}.")
                return project
        except Exception as e:
            logging.error(f"Failed to load project from {file_path}: {e}")
            return None

    def save_current_project_path(self, project):
        with open(LAST_PROJECT_SAVE, 'w', encoding='utf-8') as file:
            file.write(project.get_file_path())

    def create_and_verify_project(self, project_name, project_path):
        """Creates a new project and verifies its integrity."""
        project = Project(project_name, project_path)
        project_file_path = os.path.join(project_path, f"{project_name}.json")
        try:
            with open(project_file_path, 'w', encoding='utf-8') as file:
                json.dump({"name": project.name}, file, ensure_ascii=False, indent=4)
                self.init_database_connection(project)
                logging.info(f"Project created at {project_file_path}.")
                return project
        except Exception as e:
            logging.error(f"Failed to create project at {project_file_path}: {e}")
            return None

    def init_photo_manager(self):
        """Initializes the photo manager based on camera availability."""
        logging.info("Photo manager starting...")
        try:


            # Start asynchronous camera test in a synchronous
            camera_check = asyncio.run(check_cameras())
            if camera_check:
                self.photo_manager = PhotoManager()
                logging.info("Photo manager started.")
            else:
                logging.error("Photo_manager: No cameras found. Aborted.")
        except ImportError:
            logging.warning("PhotoManager not available, initializing PhotoManagerEmulator.")
            return PhotoManagerEmulator()

    def init_photo_manager_emulator(self):
        logging.info("Photo manager emulator starting...")
        self.photo_manager = PhotoManagerEmulator()
        logging.info("Photo manager emulator started.")
