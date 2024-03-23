import os
import sys
import logging
from src.data_base_module import DBManager
from src.types import IntervalCondition

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QScrollArea, QMainWindow, QLabel, QStackedWidget, QLineEdit, QDoubleSpinBox, QRadioButton, QCheckBox)
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QPixmap

DATA_FOLDER_PATH = os.path.join("~", ".geo_photo")
INTERVAL_STEP = 0.5
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='geo_photo_app.log')

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)


class IntervalSettings:
    def __init__(self, interval_from=0.0, interval_to=INTERVAL_STEP, is_marked=False, condition=IntervalCondition.WET):
        self.interval_from = interval_from
        self.interval_to = interval_to
        self.is_marked = is_marked
        self.condition = condition

class FocusButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)

    # override method
    def focusInEvent(self, event):
        super().focusInEvent(event)
        if isinstance(self.parent(), QWidget):
            scroll_area = self.find_parent_scroll_area(self.parent())
            if scroll_area:
                scroll_area.ensureWidgetVisible(self)

    @staticmethod
    def find_parent_scroll_area(widget):
        parent = widget.parent()
        while parent is not None:
            if isinstance(parent, QScrollArea):
                return parent
            parent = parent.parent()
        return None


class BaseInterfaceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_focus = None
        self.focusable_elements = []

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
                    self.focusable_elements[-1].setFocus()  # Переход к последней кнопке, если фокус на первой
                return True
            elif event.key() == Qt.Key_Down:
                if idx < len(self.focusable_elements) - 1:
                    self.focusable_elements[idx + 1].setFocus()
                else:
                    self.focusable_elements[0].setFocus()  # Переход к первой кнопке, если фокус на последней
                return True

        return super().eventFilter(source, event)

    def showEvent(self, event):
        super().showEvent(event)
        self.start_focus.setFocus()

    def create_back_button(self, callback):
        back_button = FocusButton("Назад")
        back_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        back_button.clicked.connect(callback)
        self.layout().addWidget(back_button)
        self.focusable_elements.append(back_button)
        self.start_focus = back_button
        return back_button


class CustomIntervalSpinBox(QHBoxLayout):
    def __init__(self, widget, event_filter):
        super().__init__(widget)

        self.spin_box = QDoubleSpinBox()
        self.spin_box.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.spin_box.setSingleStep(0.5)
        self.spin_box.setStyleSheet("""
                    QDoubleSpinBox:focus {
                        border: 2px solid #0057D9;  /* Синяя рамка */
                        background-color: #E6F4FF;  /* Светло-голубой фон */
                    }
                """)
        self.spin_box.installEventFilter(event_filter)

        self.decrease_button = QPushButton("<")
        self.decrease_button.clicked.connect(self.spin_box.stepDown)
        self.decrease_button.setStyleSheet("""
                            QPushButton {
                                background-color: #4CAF50;  /* Зелёный */
                                color: white;
                                border-radius: 10px;
                                padding: 10px 24px;
                            }
                            QPushButton:hover {
                                background-color: #45a049;
                            }
                        """)

        self.increase_button = QPushButton(">")
        self.increase_button.clicked.connect(self.spin_box.stepUp)
        self.increase_button.setStyleSheet("""
                                    QPushButton {
                                        background-color: #4CAF50;  /* Зелёный */
                                        color: white;
                                        border-radius: 10px;
                                        padding: 10px 24px;
                                    }
                                    QPushButton:hover {
                                        background-color: #45a049;
                                    }
                                """)

        self.addWidget(self.decrease_button)
        self.addWidget(self.spin_box)
        self.addWidget(self.increase_button)

        self.spin_box.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if source == self.spin_box:
                if event.key() == Qt.Key_Left:
                    self.animate_button(self.decrease_button)
                    self.spin_box.stepDown()
                    return True
                elif event.key() == Qt.Key_Right:
                    self.animate_button(self.increase_button)
                    self.spin_box.stepUp()
                    return True
        return False

    def animate_button(self, button):
        original_style_sheet = button.styleSheet()
        button.setStyleSheet("background-color: lightgray;")
        QTimer.singleShot(100, lambda: button.setStyleSheet(original_style_sheet))


class PhotoView(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, project, well, interval, photo, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.project = project
        self.well = well
        self.interval = interval
        self.photo = photo
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(lambda: self.switch_interface_callback(
            IntervalWidget,
            self.database_manager,
            self.photo_manager,
            self.project,
            self.well,
            self.interval))

        photo_label = QLabel()
        pixmap = QPixmap(self.photo["path"])
        photo_label.setPixmap(pixmap.scaled(photo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(photo_label)

    #     self.photo_label = QLabel()
    #     self.photo_label.setAlignment(Qt.AlignCenter)  # Центрируем изображение
    #     layout.addWidget(self.photo_label)
    #     self.update_photo()
    #
    # def update_photo(self):
    #     # Загрузка и масштабирование изображения с учетом текущего размера QLabel
    #     pixmap = QPixmap(self.photo["path"])
    #     self.photo_label.setPixmap(
    #         pixmap.scaled(self.photo_label.width(), self.photo_label.height(), Qt.KeepAspectRatio,
    #                       Qt.SmoothTransformation))
    #
    # def resizeEvent(self, event):
    #     # Обновляем изображение при изменении размера окна
    #     self.update_photo()
    #     super().resizeEvent(event)


class PhotoReviewWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, project, well, interval_settings, photos, switch_interface_callback,
                 parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.project = project
        self.well = well
        self.interval_settings = interval_settings
        self.photos = photos
        self.switch_interface_callback = switch_interface_callback
        self.current_photo_index = 0

        self.layout = QVBoxLayout(self)
        self.photo_label = QLabel()
        self.layout.addWidget(self.photo_label)

        buttons_layout = QHBoxLayout()

        no_button = QPushButton("Нет")
        no_button.setStyleSheet("""
                QPushButton:focus { background-color: blue; color: white; }
            """)
        no_button.clicked.connect(self.on_no_clicked)
        buttons_layout.addWidget(no_button)
        self.focusable_elements.append(no_button)

        yes_button = QPushButton("Да")
        yes_button.setStyleSheet("""
                        QPushButton:focus { background-color: blue; color: white; }
                    """)
        yes_button.clicked.connect(self.on_yes_clicked)
        buttons_layout.addWidget(yes_button)
        self.focusable_elements.append(yes_button)

        self.layout.addLayout(buttons_layout)

        self.display_current_photo()
        self.start_focus = yes_button

    def display_current_photo(self):
        pixmap = QPixmap(self.photos[self.current_photo_index])
        self.photo_label.setPixmap(pixmap.scaled(self.photo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_yes_clicked(self):
        if self.current_photo_index < len(self.photos) - 1:
            self.current_photo_index += 1
            self.display_current_photo()
        else:
            permanent_photos = ph_manager.save_photos_to_permanent_storage(
                self.project,
                self.well,
                self.interval_settings)
            result = self.database_manager.create_interval_with_photos(
                self.well["id"],
                self.interval_settings,
                permanent_photos)
            if result[0]:
                new_interval = self.database_manager.get_interval(result[1])
                self.switch_interface_callback(
                    IntervalWidget,
                    self.database_manager,
                    self.photo_manager,
                    self.project,
                    self.well,
                    new_interval)
            else:
                # TODO error msg
                self.on_no_clicked()

    def on_no_clicked(self):
        self.photo_manager.clear_temp_storage()
        self.switch_interface_callback(
            CreateIntervalWidget,
            self.database_manager,
            self.photo_manager,
            self.project,
            self.well,
            self.interval_settings)


class IntervalWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, project, well, interval, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.project = project
        self.well = well
        self.interval = interval
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(
            lambda: self.switch_interface_callback(
                WellWidget,
                self.database_manager,
                self.photo_manager,
                self.project,
                self.well))

        project_name_label = QLabel(self.project["name"])
        layout.addWidget(project_name_label)

        well_name_label = QLabel(self.well["name"])
        layout.addWidget(well_name_label)

        new_interval_label = QLabel(
            "Интервал: " + str(self.interval["interval_from"]) + ' - ' + str(self.interval["interval_to"]))
        layout.addWidget(new_interval_label)

        condition_label = QLabel(
            "Состояние: " + "Мокрый" if self.interval["condition"] == IntervalCondition.WET else "Сухой"
        )
        layout.addWidget(condition_label)

        is_marked_label = QLabel("С разметкой" if self.interval["is_marked"] else "Без разметки")
        layout.addWidget(is_marked_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_area.setWidget(scroll_container)
        scroll_layout = QVBoxLayout(scroll_container)

        photos = self.database_manager.get_all_photos_by_interval_id(self.interval["id"])
        for photo in photos:
            photo_button = FocusButton(photo["path"], scroll_container)
            photo_button.clicked.connect(
                lambda _, p=photo: self.switch_interface_callback(
                    PhotoView,
                    self.database_manager,
                    self.photo_manager,
                    self.project,
                    self.well,
                    self.interval,
                    p))
            scroll_layout.addWidget(photo_button)
            photo_button.installEventFilter(self)
            photo_button.setStyleSheet("""
                                                QPushButton:focus { background-color: blue; color: white; }
                                            """)
            self.focusable_elements.append(photo_button)

        next_interval_button = FocusButton("Следующий интервал", )
        layout.addWidget(next_interval_button)
        next_interval_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        next_interval_button.installEventFilter(self)
        next_interval_button.clicked.connect(
            lambda: self.switch_interface_callback(
                CreateIntervalWidget,
                self.database_manager,
                self.photo_manager,
                self.project,
                self.well,
                IntervalSettings(
                    self.interval["interval_to"],
                    self.interval["interval_to"] + INTERVAL_STEP,
                    self.interval["is_marked"],
                    self.interval["condition"])))
        self.focusable_elements.append(next_interval_button)
        self.start_focus = next_interval_button


class CreateIntervalWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, project, well, interval_settings, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.project = project
        self.well = well
        self.interval_settings = interval_settings
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(
            lambda: self.switch_interface_callback(
                WellWidget,
                self.database_manager,
                self.photo_manager,
                self.project,
                self.well))

        # Project label
        project_name_label = QLabel(self.project["name"])
        layout.addWidget(project_name_label)

        # Well label
        well_name_label = QLabel(self.well["name"])
        layout.addWidget(well_name_label)

        # Form name label
        form_name = QLabel("Создание нового интервала")
        layout.addWidget(form_name)

        # "Интервал От" виджет
        interval_from_widget = QWidget()
        interval_from_layout = CustomIntervalSpinBox(interval_from_widget, self)
        interval_from_layout.spin_box.setValue(self.interval_settings.interval_from)
        layout.addWidget(interval_from_widget)

        # "Интервал До" виджет
        interval_to_widget = QWidget()
        interval_to_layout = CustomIntervalSpinBox(interval_to_widget, self)
        interval_to_layout.spin_box.setValue(self.interval_settings.interval_to)
        layout.addWidget(interval_to_widget)

        # Mark check box
        is_marked_check_box = QCheckBox("С разметкой")
        layout.addWidget(is_marked_check_box)
        is_marked_check_box.setChecked(self.interval_settings.is_marked)

        # Wet radio button
        wet_radio_button = QRadioButton("Мокрый")
        layout.addWidget(wet_radio_button)

        # Dry radio button
        dry_radio_button = QRadioButton("Сухой")
        layout.addWidget(dry_radio_button)

        if self.interval_settings.condition == IntervalCondition.WET:
            wet_radio_button.setChecked(True)
        else:
            dry_radio_button.setChecked(True)

        # Set form style
        self.setStyleSheet("""
                QRadioButton {
                    font-size: 16px;
                }
                QRadioButton:focus {
                    border: 2px solid #0057D9; /* Синяя рамка вокруг радиокнопки */
                    background-color: #E6F4FF; /* Светло-голубой фон */
                }
                QCheckBox:focus {
                        border: 2px solid #0057d9;  /* Синяя рамка вокруг чекбокса при фокусировке */
                }
                """)

        # Make photo button
        make_photo_button = FocusButton("Сделать фотографии")
        layout.addWidget(make_photo_button)
        make_photo_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        make_photo_button.installEventFilter(self)
        make_photo_button.clicked.connect(
            lambda: self.make_photo(
                IntervalSettings(
                    interval_from_layout.spin_box.value(),
                    interval_to_layout.spin_box.value(),
                    is_marked_check_box.isChecked(),
                    IntervalCondition.WET if wet_radio_button.isChecked() else IntervalCondition.DRY
                    )))

        self.focusable_elements.append(interval_from_layout.spin_box)
        self.focusable_elements.append(interval_to_layout.spin_box)
        self.focusable_elements.append(is_marked_check_box)
        self.focusable_elements.append(wet_radio_button)
        self.focusable_elements.append(dry_radio_button)
        self.focusable_elements.append(make_photo_button)

        self.start_focus = make_photo_button

    def make_photo(self, interval_settings):
        photos = self.photo_manager.take_photos(self.project, self.well, interval_settings)
        self.switch_interface_callback(
            PhotoReviewWidget, 
            self.database_manager,
            self.photo_manager,
            self.project,
            self.well,
            interval_settings,
            photos)


class WellWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, project, well, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.project = project
        self.well = well
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        intervals = self.database_manager.get_all_intervals_by_well_id(self.well["id"])

        self.create_back_button(
            lambda: self.switch_interface_callback(
                ProjectWidget,
                self.database_manager,
                self.photo_manager,
                self.project))

        project_name_label = QLabel(self.project["name"])
        layout.addWidget(project_name_label)

        well_name_label = QLabel(self.well["name"])
        layout.addWidget(well_name_label)

        label = QLabel("Выбор интервала")
        layout.addWidget(label)

        new_interval_button = FocusButton("Новый интервал")
        layout.addWidget(new_interval_button)
        new_interval_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        new_interval_button.installEventFilter(self)

        new_interval_button.clicked.connect(
            lambda: self.switch_interface_callback(
                CreateIntervalWidget,
                self.database_manager,
                self.photo_manager,
                self.project,
                self.well,
                IntervalSettings(
                    float(intervals[-1]["interval_to"]),
                    float(intervals[-1]["interval_to"]) + INTERVAL_STEP,
                    intervals[-1]["is_marked"],
                    intervals[-1]["condition"]) if intervals else IntervalSettings()
            )
        )
        self.focusable_elements.append(new_interval_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_area.setWidget(scroll_container)
        scroll_layout = QVBoxLayout(scroll_container)

        for interval in intervals:
            interval_button = FocusButton(str(interval["interval_from"]) + ' - ' + str(interval["interval_to"]),
                                          scroll_container)
            interval_button.clicked.connect(
                lambda _, i=interval: self.switch_interface_callback(
                    IntervalWidget, self.database_manager, self.photo_manager, self.project, self.well, i))
            scroll_layout.addWidget(interval_button)
            interval_button.installEventFilter(self)
            interval_button.setStyleSheet("""
                                                QPushButton:focus { background-color: blue; color: white; }
                                            """)
            self.focusable_elements.append(interval_button)


class CreateWellWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, project, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.project = project
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(
            lambda: self.switch_interface_callback(
                ProjectWidget,
                self.database_manager,
                self.photo_manager,
                self.project))

        # Метка "Создание новой скважины"
        create_well_label = QLabel("Создание новой скважины")
        layout.addWidget(create_well_label)

        # Поле ввода "Название скважины"
        well_name_input = QLineEdit()
        well_name_input.setPlaceholderText("Название скважины")
        layout.addWidget(well_name_input)

        # Кнопка "Создать"
        create_well_button = QPushButton("Создать")
        layout.addWidget(create_well_button)
        create_well_button.setStyleSheet("""
                                        QPushButton:focus { background-color: blue; color: white; }
                                    """)
        create_well_button.clicked.connect(
            lambda: self.create_well(well_name_input.text()))

        # Подключение фокуса
        self.focusable_elements.append(well_name_input)
        self.focusable_elements.append(create_well_button)

    def create_well(self, well_name):
        new_well = self.database_manager.add_well(well_name, self.project["id"])
        self.switch_interface_callback(
            WellWidget,
            self.database_manager,
            self.photo_manager,
            self.project,
            new_well)


class CreateProjectWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(
            lambda: self.switch_interface_callback(
                ChooseProjectWidget,
                self.database_manager))

        create_project_label = QLabel("Новый проект")
        layout.addWidget(create_project_label)

        project_name_input = QLineEdit()
        project_name_input.setPlaceholderText("Название проекта")
        layout.addWidget(project_name_input)
        self.focusable_elements.append(project_name_input)

        create_project_button = QPushButton("Создать")
        layout.addWidget(create_project_button)
        create_project_button.setStyleSheet("""
                                        QPushButton:focus { background-color: blue; color: white; }
                                    """)
        create_project_button.clicked.connect(
            lambda: self.create_project(project_name_input.text()))
        self.focusable_elements.append(create_project_button)

        self.install_focus_event_filters()

    def create_project(self, project_name):
        new_project = self.database_manager.add_project(project_name)
        self.switch_interface_callback(
            ProjectWidget,
            self.database_manager,
            self.photo_manager,
            new_project)


class ProjectWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, project, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.project = project
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(
            lambda: self.switch_interface_callback(
                ChooseProjectWidget,
                self.database_manager,
                self.photo_manager))

        project_name_label = QLabel(self.project["name"])
        layout.addWidget(project_name_label)

        label = QLabel("Выбор скважины")
        layout.addWidget(label)

        new_well_button = FocusButton("Новая скважина")
        new_well_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        new_well_button.clicked.connect(
            lambda: self.switch_interface_callback(
                CreateWellWidget,
                self.database_manager,
                self.photo_manager,
                self.project)
        )
        layout.addWidget(new_well_button)
        self.focusable_elements.append(new_well_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_area.setWidget(scroll_container)
        scroll_layout = QVBoxLayout(scroll_container)

        wells = self.database_manager.get_all_wells_by_project_id(self.project["id"])
        for well in wells:
            well_button = FocusButton(well["name"], scroll_container)
            well_button.clicked.connect(
                lambda _, w=well: self.switch_interface_callback(
                    WellWidget,
                    self.database_manager,
                    self.photo_manager,
                    self.project,
                    w))
            scroll_layout.addWidget(well_button)
            well_button.setStyleSheet("""
                                        QPushButton:focus { background-color: blue; color: white; }
                                    """)
            self.focusable_elements.append(well_button)


class ChooseProjectWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, photo_manager, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.photo_manager = photo_manager
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        project_selection_label = QLabel("Выбор проекта")
        layout.addWidget(project_selection_label)

        new_project_button = FocusButton("Новый проект")
        layout.addWidget(new_project_button)
        new_project_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        new_project_button.clicked.connect(
            lambda: self.switch_interface_callback(CreateProjectWidget, self.database_manager, self.photo_manager)
        )
        self.focusable_elements.append(new_project_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_area.setWidget(scroll_container)
        scroll_layout = QVBoxLayout(scroll_container)

        projects = self.database_manager.get_all_projects()
        for project in projects:
            project_button = FocusButton(project["name"], scroll_container)
            project_button.clicked.connect(
                lambda _, p=project: self.switch_interface_callback(ProjectWidget, self.database_manager, self.photo_manager, p))
            scroll_layout.addWidget(project_button)
            project_button.setStyleSheet("""
                                QPushButton:focus { background-color: blue; color: white; }
                            """)
            self.focusable_elements.append(project_button)

        self.start_focus = new_project_button


class MainWindow(QMainWindow):
    def __init__(self, database_manager, photo_manager):
        super().__init__()
        self.setWindowTitle("GeoPhoto")

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создание и добавление главного интерфейса
        self.main_widget = ChooseProjectWidget(database_manager, photo_manager, self.switch_interface)
        self.stacked_widget.addWidget(self.main_widget)

    def switch_interface(self, interface_class, *args, **kwargs):
        widget = interface_class(*args, **kwargs, switch_interface_callback=self.switch_interface, parent=None)
        self.clean_stacked_widget()
        self.stacked_widget.addWidget(widget)
        self.stacked_widget.setCurrentWidget(widget)

    def clean_stacked_widget(self):
        while self.stacked_widget.count() > 0:
            widget_to_remove = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()


if __name__ == '__main__':
    sys.excepthook = handle_exception

    if not os.path.exists(DATA_FOLDER_PATH):
        os.makedirs(DATA_FOLDER_PATH)

    db_manager = DBManager(DATA_FOLDER_PATH)

    ph_manager = None
    try:
        logging.info(f"Trying to start photo manager")
        from src.photo_module import PhotoModule
        ph_manager = PhotoModule()
        logging.info(f"Photo manager stated.")
    except Exception as e:
        logging.error(f"Failed to initialize photo manager: {e}")

    if ph_manager is None:
        logging.info(f"Trying to start photo manager EMULATOR")
        from src.photo_module_emulator import PhotoModuleEmulator
        ph_manager = PhotoModuleEmulator()
        logging.info(f"Photo manager EMULATOR stated.")

    ph_manager.clear_temp_storage()

    app = QApplication(sys.argv)

    window = MainWindow(db_manager, ph_manager)
    window.showFullScreen()

    logging.info("App started")

    app.aboutToQuit.connect(db_manager.close_connection)
    sys.exit(app.exec_())
