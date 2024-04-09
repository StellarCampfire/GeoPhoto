import json
import logging
import os

from PyQt5.QtWidgets import QApplication
from src.core.window_types import WindowType
from src.models.project import Project

from src.utils.data_base_manager import DataBaseManager
from src.utils.photo_manager.photo_manager_emulator import PhotoManagerEmulator

from src.windows.start_window import StartWindow
from src.windows.interval_window import IntervalWindow
from src.windows.new_interval_window import NewIntervalWindow
from src.windows.new_project_window import NewProjectWindow
from src.windows.new_well_window import NewWellWindow
from src.windows.photo_review_window import PhotoReviewWindow
from src.windows.photo_view_window import PhotoViewWindow
from src.windows.project_window import ProjectWindow
from src.windows.well_window import WellWindow
from src.windows.settings_window import SettingsWindow


class App(QApplication):
    def __init__(self, sys_argv, config_manager, emulate=False, resolution=None):
        logging.debug("Initializing the application.")
        super().__init__(sys_argv)
        self.current_window = None
        self.resolution = resolution
        self.config_manager = config_manager
        self.switch_interface(WindowType.START_WINDOW)
        self.db_manager = None
        self.photo_manager = None

        if emulate:
            self.init_photo_manager_emulator()
        else:
            self.init_photo_manager()

    def switch_interface(self, window_type, *args, **kwargs):
        if self.current_window is not None:
            self.current_window.close()
        self.current_window = self.create_window(window_type, *args, **kwargs)
        self.adjust_window_display()
        logging.info(f"Window {window_type} is now visible.")

    def adjust_window_display(self):
        if self.resolution:
            width, height = map(int, self.resolution.split('x'))
            self.current_window.setGeometry(100, 100, width, height)
        else:
            self.current_window.showFullScreen()
        self.current_window.show()

    def create_window(self, window_type, *args, **kwargs):
        logging.debug(f"Creating a new window of type {window_type}.")
        if window_type == WindowType.START_WINDOW:
            return StartWindow(self, *args, **kwargs)
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
        elif window_type == WindowType.SETTINGS_WINDOW:
            return SettingsWindow(self, *args, **kwargs)
        else:
            logging.error(f"Unknown window type: {window_type}")
            raise ValueError(f"Unknown window type: {window_type}")

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
                project = Project.from_dict(project_data)
                self.init_database_connection(project)
                logging.info(f"Project loaded and database initialized for {project.name}.")
                return project
        except Exception as e:
            logging.error(f"Failed to load project from {file_path}: {e}")
            return None

    def create_and_verify_project(self, project_name, project_path):
        """Creates a new project and verifies its integrity."""
        project = Project(project_name, project_path)
        project_file_path = os.path.join(project_path, f"{project_name}.json")
        try:
            with open(project_file_path, 'w', encoding='utf-8') as file:
                json.dump(project.to_dict(), file, ensure_ascii=False, indent=4)
                self.init_database_connection(project)
                logging.info(f"Project created at {project_file_path}.")
                return project
        except Exception as e:
            logging.error(f"Failed to create project at {project_file_path}: {e}")
            return None

    def init_photo_manager(self):
        """Initializes the photo manager based on camera availability."""
        logging.info("Photo manager emulator starting...")
        try:
            from src.utils.photo_manager.photo_manager import PhotoManager
            if PhotoManager.check_cameras():
                self.photo_manager = PhotoManager()
                logging.info("Photo manager emulator started.")
            else:
                logging.error("Photo_manager: No cameras found. Aborted.")
        except ImportError:
            logging.warning("Picamera2 not available, initializing PhotoManagerEmulator.")
            return PhotoManagerEmulator()

    def init_photo_manager_emulator(self):
        logging.info("Photo manager emulator starting...")
        self.photo_manager = PhotoManagerEmulator()
        logging.info("Photo manager emulator started.")


