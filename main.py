import os
import sys
import json
import logging
from logger_config import setup_logging
from src.data_base_module import DBManager
from src.models import IntervalSettings, IntervalCondition, Project, Well, Interval, Photo

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QScrollArea, QMainWindow, QLabel, QStackedWidget, QLineEdit, QDoubleSpinBox,
                             QRadioButton, QCheckBox, QFileDialog, QSpacerItem, QSizePolicy, QGraphicsScene)
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QPixmap

from PyQt5.QtCore import QEvent, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QWidget, QSpinBox, QPushButton, QHBoxLayout

from resources.py.StartForm import Ui_StartForm
from resources.py.NewProjectForm import Ui_NewProjectForm
from resources.py.ProjectForm import Ui_ProjectForm
from resources.py.NewWellForm import Ui_NewWellForm
from resources.py.WellForm import Ui_WellForm
from resources.py.IntervalForm import Ui_IntervalForm
from resources.py.NewIntervalForm import Ui_NewIntervalForm
from resources.py.PhotoReviewForm import Ui_PhotoReviewForm
from resources.py.PhotoViewForm import Ui_PhotoViewForm
from resources.py.SattingsForm import Ui_SettingsForm

INTERVAL_STEP = 0.5


def load_styles_from_file(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        return file.read()


class BaseWindow(QMainWindow):
    def __init__(self, app_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app_instance
        self.start_focus = None
        self.focusable_elements = []

        # Создание и установка centralwidget
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

    def install_focus_event_filters(self):
        for element in self.focusable_elements:
            element.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source in self.focusable_elements:
            idx = self.focusable_elements.index(source)

            if event.key() == Qt.Key_Up:
                if idx > 0:
                    self.focusable_elements[idx - 1].setFocus()
                else:
                    self.focusable_elements[-1].setFocus()
                return True
            elif event.key() == Qt.Key_Down:
                if idx < len(self.focusable_elements) - 1:
                    self.focusable_elements[idx + 1].setFocus()
                else:
                    self.focusable_elements[0].setFocus()
                return True
            elif isinstance(source, QDoubleSpinBox) and (event.key() in [Qt.Key_Left, Qt.Key_Right]):
                pass

        # Для всех остальных событий пропускаем обработку через базовый класс
        return super().eventFilter(source, event)

    def showEvent(self, event):
        super().showEvent(event)
        if self.start_focus is not None:
            self.start_focus.setFocus()

    def switch_interface(self, interface_class, *args, **kwargs):
        self.app.switch_interface(interface_class, *args, **kwargs)

    def get_database_manager(self):
        return self.app.db_manager

    def get_photo_manager(self):
        return self.app.photo_manager


class CustomSpinBox(QWidget):
    def __init__(self, spin_box, decrease_button, increase_button, parent=None):
        super().__init__(parent)

        self.style = load_styles_from_file(os.path.join('resources', 'styles', 'style.qss'))

        self.spin_box = spin_box
        self.decrease_button = decrease_button
        self.increase_button = increase_button

        self.decrease_button.clicked.connect(self.decrease)
        self.increase_button.clicked.connect(self.increase)

        self.spin_box.installEventFilter(self)

        self.decrease_button.setProperty("class", "CustomSpinboxButton")
        self.increase_button.setProperty("class", "CustomSpinboxButton")
        self.applyStyles()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source == self.spin_box:
            if event.key() == Qt.Key_Left:
                self.decrease_button.click()
                return True
            elif event.key() == Qt.Key_Right:
                self.increase_button.click()
                return True
            elif event.key() in (Qt.Key_Up, Qt.Key_Down):
                return False
        return super().eventFilter(source, event)

    def applyStyles(self):
        self.spin_box.setStyleSheet(self.style)
        self.decrease_button.setStyleSheet(self.style)
        self.increase_button.setStyleSheet(self.style)

    def animate_button_press(self, button):
        button.setProperty("class", "CustomSpinboxButtonPressed")
        self.applyStyles()
        QTimer.singleShot(100, lambda: self.reset_button_style(button))

    def reset_button_style(self, button):
        button.setProperty("class", "CustomSpinboxButton")
        self.applyStyles()

    def increase(self):
        self.animate_button_press(self.increase_button)
        self.spin_box.stepUp()

    def decrease(self):
        self.animate_button_press(self.decrease_button)
        self.spin_box.stepDown()

    def setSingleStep(self, step):
        self.spin_box.setSingleStep(step)

    def value(self):
        return self.spin_box.value()

    def setValue(self, value):
        self.spin_box.setValue(value)


class PhotoReviewWindow(BaseWindow):
    def __init__(self, project, well, interval_settings, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.project = project
        self.well = well
        self.interval_settings = interval_settings

        self.photos = self.get_photo_manager().take_photos(self.project, self.well, self.interval_settings)
        self.current_photo_index = 0

        self.ui = Ui_PhotoReviewForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.yes_pushButton.clicked.connect(self.on_yes_clicked)
        self.ui.no_pushButton.clicked.connect(self.on_no_clicked)



    def on_yes_clicked(self):
        if self.current_photo_index < len(self.photos) - 1:
            self.current_photo_index += 1
            self.load_image()
        else:
            permanent_photos = self.get_photo_manager().save_photos_to_permanent_storage(
                self.project,
                self.well,
                self.interval_settings)
            result = self.get_database_manager().create_interval_with_photos(
                self.well.id,
                self.interval_settings,
                permanent_photos)
            if result[0]:
                new_interval = self.get_database_manager().get_interval(result[1])
                self.switch_interface(
                    IntervalWindow,
                    self.project,
                    self.well,
                    new_interval)
            else:
                # TODO error msg
                self.on_no_clicked()

    def on_no_clicked(self):
        self.get_photo_manager().clear_temp_storage()
        self.switch_interface(
            NewIntervalWindow,
            self.project,
            self.well,
            self.interval_settings)

    def load_image(self):
        pixmap = QPixmap(self.photos[self.current_photo_index])
        scaled_pixmap = pixmap.scaled(self.ui.photo_label.size(), Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation)
        self.ui.photo_label.setPixmap(scaled_pixmap)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'ui'):
            self.load_image()


class NewIntervalWindow(BaseWindow):
    def __init__(self, project, well, interval_settings, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_NewIntervalForm()
        self.ui.setupUi(self.centralwidget)

        self.project = project
        self.well = well
        self.interval_settings = interval_settings

        self.ui.project_name_label.setText(self.project.name)
        self.ui.well_name_label.setText(self.well.name)

        self.ui.back_button.clicked.connect(
            lambda: self.switch_interface(WellWindow, self.project, self.well))

        self.custom_interval_from = CustomSpinBox(
            self.ui.interval_from_doubleSpinBox,
            self.ui.interval_from_decrease_button,
            self.ui.interval_from_increase_button)

        self.custom_interval_to = CustomSpinBox(
            self.ui.interval_to_doubleSpinBox,
            self.ui.interval_to_decrease_button,
            self.ui.interval_to_increase_button
        )

        self.custom_interval_from.setSingleStep(0.05)
        self.custom_interval_to.setSingleStep(0.05)

        self.custom_interval_from.setValue(self.interval_settings.interval_from)
        self.custom_interval_to.setValue(self.interval_settings.interval_to)

        self.ui.is_marked_checkBox.setChecked(self.interval_settings.is_marked)
        if self.interval_settings.condition == IntervalCondition.WET:
            self.ui.wet_radioButton.setChecked(True)
        else:
            self.ui.dry_radioButton.setChecked(True)

        self.ui.create_new_interval_button.clicked.connect(self.onCreateNewIntervalClicked)

        self.focusable_elements.append(self.ui.back_button)
        self.focusable_elements.append(self.ui.interval_from_doubleSpinBox)
        self.focusable_elements.append(self.ui.interval_to_doubleSpinBox)
        self.focusable_elements.append(self.ui.is_marked_checkBox)
        self.focusable_elements.append(self.ui.wet_radioButton)
        self.focusable_elements.append(self.ui.dry_radioButton)
        self.focusable_elements.append(self.ui.create_new_interval_button)

        self.install_focus_event_filters()
        self.start_focus = self.ui.back_button

    def onCreateNewIntervalClicked(self):
        interval_from = self.ui.interval_from_doubleSpinBox.value()
        interval_to = self.ui.interval_to_doubleSpinBox.value()
        is_marked = self.ui.is_marked_checkBox.isChecked()
        condition = IntervalCondition.WET if self.ui.wet_radioButton.isChecked() else IntervalCondition.DRY
        self.make_photo(IntervalSettings(interval_from, interval_to, is_marked, condition))

    def make_photo(self, interval_settings):
        # photos = self.photo_manager.take_photos(self.project, self.well, interval_settings)
        self.switch_interface(
            PhotoReviewWindow,
            self.project,
            self.well,
            interval_settings,
            # photos
        )


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


class IntervalWindow(BaseWindow):
    def __init__(self, project, well, interval, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.project = project
        self.well = well
        self.interval = interval

        self.ui = Ui_IntervalForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.project_name_label.setText(self.project.name)
        self.ui.well_name_label.setText(self.well.name)

        self.ui.back_button.clicked.connect(lambda: self.switch_interface(
            WellWindow,
            self.project,
            self.well
        ))

        self.ui.next_interval_pushButton.clicked.connect(lambda: self.switch_interface(
            NewIntervalWindow,
            self.project,
            self.well,
            IntervalSettings(
                self.interval.interval_to,
                self.interval.interval_to + INTERVAL_STEP,
                self.interval.is_marked,
                self.interval.condition)))

        self.focusable_elements.append(self.ui.back_button)

        photos = self.get_database_manager().get_all_photos_by_interval_id(self.interval.id)
        for photo in photos:
            photo_button = QPushButton(photo.name)
            self.ui.photos_buttons_verticalLayout.layout().addWidget(photo_button)
            self.focusable_elements.append(photo_button)
            photo_button.clicked.connect(lambda _, p=photo: self.switch_interface(PhotoViewWindow, self.project, self.well, self.interval, p))
            self.focusable_elements.append(photo_button)

        self.focusable_elements.append(self.ui.next_interval_pushButton)


class PhotoViewWindow(BaseWindow):
    def __init__(self, project, well, interval, photo, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.project = project
        self.well = well
        self.interval = interval
        self.photo = photo

        self.ui = Ui_PhotoViewForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.back_pushButton.clicked.connect(
            lambda: self.switch_interface(IntervalWindow, self.project, self.well, self.interval))

    def load_image(self):
        pixmap = QPixmap(self.photo.path)
        scaled_pixmap = pixmap.scaled(self.ui.photo_label.size(), Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation)
        self.ui.photo_label.setPixmap(scaled_pixmap)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'ui'):
            self.load_image()


class WellWindow(BaseWindow):
    def __init__(self, project, well, app_instance, parent=None):
        super().__init__(app_instance, parent)
        self.ui = Ui_WellForm()
        self.ui.setupUi(self.centralwidget)

        self.project = project
        self.well = well

        self.ui.project_name_input.setText(project.name)
        self.ui.well_name_input.setText(self.well.name)

        self.ui.new_interval_button.clicked.connect(lambda: self.switch_interface(
            NewIntervalWindow,
            self.project,
            self.well,
            IntervalSettings(
                float(intervals[-1].interval_to),
                float(intervals[-1].interval_to) + INTERVAL_STEP,
                intervals[-1].is_marked,
                intervals[-1].condition) if intervals else IntervalSettings()
        ))

        self.ui.back_button.clicked.connect(lambda: self.switch_interface(ProjectWindow, self.project))

        self.focusable_elements.append(self.ui.back_button)

        intervals = self.get_database_manager().get_all_intervals_by_well_id(self.well.id)
        for interval in intervals:
            interval_button = QPushButton(interval.get_full_name())
            self.ui.intervals_buttons_verticalLayout.layout().addWidget(interval_button)
            self.focusable_elements.append(interval_button)
            interval_button.clicked.connect(lambda _, i=interval: self.switch_interface(
                IntervalWindow,
                self.project,
                self.well,
                i))

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui.intervals_buttons_verticalLayout.addItem(spacer)

        self.start_focus = self.ui.back_button


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

class SettingsWindow(BaseWindow):
    def __init__(self, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.ui = Ui_SettingsForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.sutter_speed_spinBox.setMinimum(37)
        self.ui.sutter_speed_spinBox.setMaximum(100000)
        self.ui.sutter_speed_spinBox.setValue(1000)

        self.ui.iso_spinBox.setMinimum(0)
        self.ui.iso_spinBox.setMaximum(100)
        self.ui.iso_spinBox.setValue(1)

        self.ui.back_pushButton.clicked.connect(lambda: self.switch_interface(StartWindow))

        self.ui.take_photo_camera.clicked.connect(self.set_controls_and_show_photo)

    def set_controls_and_show_photo(self):
        photo_path = self.get_photo_manager().set_controls_and_take_photo(
            Project('test_project', './'),
            Well(0, 'test_well'), IntervalSettings(),
            self.ui.sutter_speed_spinBox.value(),
            self.ui.iso_spinBox.value())


class SettingsPreviewPhoto(BaseWindow):
    def __init__(self, photo_path, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.photo_path = photo_path

        self.ui = Ui_PhotoViewForm()
        self.ui.setupUi(self.centralwidget)

        self.ui.back_pushButton.clicked.connect(
            lambda: self.switch_interface(SettingsWindow))

    def load_image(self):
        pixmap = QPixmap(self.photo_path)
        scaled_pixmap = pixmap.scaled(self.ui.photo_label.size(), Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation)
        self.ui.photo_label.setPixmap(scaled_pixmap)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'ui'):
            self.load_image()



class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = None
        self.photo_manager = None
        try:
            logging.info(f"Trying to start photo manager")
            from src.photo_module import PhotoModule
            self.photo_manager = PhotoModule()
            logging.info(f"Photo manager stated.")
            self.photo_manager.get_exposure_settins_value()
        except Exception as e:
            logging.error(f"Failed to initialize photo manager: {e}")

        if self.photo_manager is None:
            logging.info(f"Trying to start photo manager EMULATOR")
            from src.photo_module_emulator import PhotoModuleEmulator
            self.photo_manager = PhotoModuleEmulator()
            logging.info(f"Photo manager EMULATOR stated.")

        self.photo_manager.clear_temp_storage()

        self.stackedWidget = QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        self.switch_interface(StartWindow)

    def switch_interface(self, interface_class, *args, **kwargs):
        widget = interface_class(
            *args,
            app_instance=self,
            **kwargs)
        self.clean_stacked_widget()
        self.stackedWidget.addWidget(widget)
        self.stackedWidget.setCurrentWidget(widget)

    def clean_stacked_widget(self):
        while self.stackedWidget.count() > 0:
            widget_to_remove = self.stackedWidget.widget(0)
            self.stackedWidget.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

    def init_database_connection(self, project):
        self.db_manager = DBManager(project)

    def close_database_connection(self):
        if self.db_manager is not None:
            self.db_manager.close_connection()
            self.db_manager = None

    def create_and_verify_project(self, project_name, project_path):
        project = Project(project_name, project_path)

        project_file_name = f"{project_name}.json"
        project_file_path = os.path.join(project_path, project_file_name)

        with open(project_file_path, "w", encoding='utf-8') as project_file:
            json.dump(project.to_dict(), project_file, ensure_ascii=False, indent=4)

        logging.info(f"Project '{project.name}' created at '{project_file_path}'.")

        # Попытка загрузить JSON обратно для проверки
        try:
            with open(project_file_path, "r", encoding='utf-8') as project_file:
                loaded_project_data = json.load(project_file)
                assert loaded_project_data == project.to_dict(), "Loaded project data does not match saved data."
                logging.info("JSON file has been successfully verified.")
                self.init_database_connection(project)
                return project
        except AssertionError as error:
            logging.error(f"Verification failed: {error}")
        except Exception as e:
            logging.error(f"An error occurred while trying to verify the JSON file: {str(e)}")

        return None

    def load_project_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as project_file:
                project_data = json.load(project_file)

            project = Project.from_dict(project_data)
            logging.info(f"Project '{project.name}' loaded from '{file_path}'.")
            self.init_database_connection(project)
            return project

        except json.JSONDecodeError:
            logging.error(f"Could not deserialize file {file_path}, file content is not valid JSON")
        except FileNotFoundError:
            logging.error(f"File {file_path} not found")
        except ValueError as e:
            logging.error(f"Error while deserializing file {file_path}: {e}")
        except Exception as e:
            logging.error(f"An error occurred while loading the project file {file_path}: {e}")

        return None


if __name__ == '__main__':
    setup_logging()

    app = QApplication(sys.argv)

    window = App()
    window.showFullScreen()
    # window.show()

    logging.info("App started")

    sys.exit(app.exec_())
