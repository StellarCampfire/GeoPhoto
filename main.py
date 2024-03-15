import os
import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QScrollArea, QMainWindow, QLabel, QStackedWidget, QLineEdit, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QPixmap

DATA_FOLDER_PATH = 'data'


class GeoPhotoDBManager:
    def __init__(self):
        db_path = os.path.join("data", "geo_photo_database.db")
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.setup_database()

    def setup_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Projects(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Wells(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            FOREIGN KEY(project_id) REFERENCES Projects(id) ON DELETE CASCADE
            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Intervals(
            id INTEGER PRIMARY KEY,
            interval_from REAL NOT NULL,
            interval_to REAL NOT NULL,
            well_id INTEGER NOT NULL,
            FOREIGN KEY(well_id) REFERENCES Wells(id) ON DELETE CASCADE
            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Photos(
            id INTEGER PRIMARY KEY,
            photo_path TEXT NOT NULL,
            interval_id INTEGER NOT NULL,
            order_num INTEGER,
            FOREIGN KEY(interval_id) REFERENCES Intervals(id) ON DELETE CASCADE
            )''')
        self.connection.commit()

    def add_project(self, name):
        self.cursor.execute("INSERT INTO Projects (name) VALUES (?)", (name,))
        self.connection.commit()
        project_id = self.cursor.lastrowid
        return self.get_project(project_id)

    def delete_project(self, project_id):
        self.cursor.execute("DELETE FROM Projects WHERE id = ?", (str(project_id),))
        self.connection.commit()

    def update_project(self, project_id, new_name):
        self.cursor.execute("UPDATE Projects SET name = ? WHERE id = ?", (new_name, str(project_id)))
        self.connection.commit()

    def get_project(self, project_id):
        self.cursor.execute("SELECT * FROM Projects WHERE id = ?", (str(project_id),))
        project_data = self.cursor.fetchone()
        if project_data:
            project = {
                'id': project_data[0],
                'name': project_data[1]
            }
            return project
        else:
            return None

    def get_all_projects(self):
        self.cursor.execute("SELECT * FROM Projects")
        projects_data = self.cursor.fetchall()
        projects = []
        for project_row in projects_data:
            project = {
                'id': project_row[0],
                'name': project_row[1]
            }
            projects.append(project)
        return projects

    def add_well(self, name, project_id):
        self.cursor.execute("INSERT INTO Wells (name, project_id) VALUES (?, ?)", (name, str(project_id)))
        self.connection.commit()
        well_id = self.cursor.lastrowid
        return self.get_well(well_id)

    def delete_well(self, well_id):
        self.cursor.execute("DELETE FROM Wells WHERE id = ?", str(well_id))
        self.connection.commit()

    def update_well(self, well_id, new_name):
        self.cursor.execute("UPDATE Wells SET name = ? WHERE id = ?", (new_name, str(well_id)))
        self.connection.commit()

    def get_well(self, well_id):
        self.cursor.execute("SELECT * FROM Wells WHERE id = ?", str(well_id))
        well_data = self.cursor.fetchone()
        if well_data:
            well = {
                'id': well_data[0],
                'name': well_data[1],
                'project_id': well_data[2]
            }
            return well
        else:
            return None

    def get_all_wells_by_project_id(self, project_id):
        self.cursor.execute("SELECT * FROM Wells WHERE project_id = ?", str(project_id))
        wells_data = self.cursor.fetchall()
        wells = []
        for well_row in wells_data:
            well = {
                'id': well_row[0],
                'name': well_row[1],
                'project_id': well_row[2]
            }
            wells.append(well)
        return wells

    def add_interval(self, interval_from, interval_to, well_id):
        self.cursor.execute("INSERT INTO Intervals (interval_from, interval_to, well_id) VALUES (?, ?, ?)",
                            (str(interval_from), str(interval_to), str(well_id)))
        self.connection.commit()
        interval_id = self.cursor.lastrowid
        return self.get_interval(interval_id)

    def delete_interval(self, interval_id):
        self.cursor.execute("DELETE FROM Intervals WHERE id = ?", (str(interval_id),))
        self.connection.commit()

    def update_interval(self, interval_id, new_from, new_to):
        self.cursor.execute("UPDATE Intervals SET interval_from = ?, interval_to = ? WHERE id = ?",
                            (new_from, new_to, str(interval_id)))
        self.connection.commit()

    def get_interval(self, interval_id):
        self.cursor.execute("SELECT * FROM Intervals WHERE id = ?", (str(interval_id),))
        interval_data = self.cursor.fetchone()
        if interval_data:
            interval = {
                'id': interval_data[0],
                'interval_from': interval_data[1],
                'interval_to': interval_data[2],
                'well_id': interval_data[3]
            }
            return interval
        else:
            return None

    def get_all_intervals_by_well_id(self, well_id):
        self.cursor.execute("SELECT * FROM Intervals WHERE well_id = ?", str(well_id))
        intervals_data = self.cursor.fetchall()
        intervals = []
        for interval_row in intervals_data:
            interval = {
                'id': interval_row[0],
                'interval_from': interval_row[1],
                'interval_to': interval_row[2],
                'well_id': interval_row[2]
            }
            intervals.append(interval)
        return intervals

    def add_photo(self, photo_path, interval_id, order_num):
        self.cursor.execute("INSERT INTO Photos (photo_path, interval_id, order_num) VALUES (?, ?, ?)",
                            (photo_path, str(interval_id), str(order_num)))
        self.connection.commit()

    def delete_photo(self, photo_id):
        self.cursor.execute("DELETE FROM Photos WHERE id = ?", (str(photo_id),))
        self.connection.commit()

    def update_photo(self, photo_id, new_path, new_order):
        self.cursor.execute("UPDATE Photos SET photo_path = ?, order_num = ? WHERE id = ?",
                            (new_path, str(new_order), str(photo_id)))
        self.connection.commit()

    def get_photo(self, photo_id):
        self.cursor.execute("SELECT * FROM Photos WHERE id = ?", (str(photo_id),))
        photo_data = self.cursor.fetchone()
        if photo_data:
            photo = {
                'id': photo_data[0],
                'path': photo_data[1],
                'interval_id': photo_data[2]
            }
            return photo
        else:
            return None

    def get_all_photos_by_interval_id(self, interval_id):
        self.cursor.execute("SELECT * FROM Photos WHERE interval_id = ?", str(interval_id))
        photos_data = self.cursor.fetchall()
        photos = []
        for photo_row in photos_data:
            photo = {
                'id': photo_row[0],
                'path': photo_row[1],
            }
            photos.append(photo)
        return photos

    def create_interval_with_photos(self, interval_from, interval_to, well_id, photo_paths):
        try:
            self.connection.execute("BEGIN")  # Начало транзакции
            self.cursor.execute("INSERT INTO Intervals (interval_from, interval_to, well_id) VALUES (?, ?, ?)",
                                (interval_from, interval_to, well_id))
            interval_id = self.cursor.lastrowid  # Получаем ID только что созданного интервала

            for order_num, photo_path in enumerate(photo_paths, start=1):
                self.cursor.execute("INSERT INTO Photos (photo_path, interval_id, order_num) VALUES (?, ?, ?)",
                                    (photo_path, interval_id, order_num))

            self.connection.commit()  # Подтверждаем транзакцию, если все запросы выполнены успешно

            return interval_id  # Возвращаем ID созданного интервала после успешной транзакции
        except sqlite3.Error as e:
            print(f"Ошибка при создании интервала {str(interval_from)} - {str(interval_to)} с фотографиями: {e}")
            self.connection.rollback()  # Откатываем транзакцию в случае ошибки
            return None

    def close_connection(self):
        self.connection.close()


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

class PhotoReviewWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, project, well, interval_from, interval_to, photos, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.project = project
        self.well = well
        self.interval_from = interval_from
        self.interval_to = interval_to
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
        self.start_focus = no_button

    def display_current_photo(self):
        pixmap = QPixmap(self.photos[self.current_photo_index])
        self.photo_label.setPixmap(pixmap.scaled(self.photo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_yes_clicked(self):
        if self.current_photo_index < len(self.photos) - 1:
            self.current_photo_index += 1
            self.display_current_photo()
        else:
            new_interval_id = self.database_manager.create_interval_with_photos(self.interval_from, self.interval_to, self.well["id"], self.photos)
            new_interval = self.database_manager.get_interval(new_interval_id)
            self.switch_interface_callback(IntervalWidget, self.database_manager, self.project, self.well, new_interval)

    def on_no_clicked(self):
        self.switch_interface_callback(CreateIntervalWidget, self.database_manager, self.project, self.well)


class IntervalWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, project, well, interval, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
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
                self.project,
                self.well))

        project_name_label = QLabel(self.project["name"])
        layout.addWidget(project_name_label)

        well_name_label = QLabel(self.well["name"])
        layout.addWidget(well_name_label)

        new_interval_label = QLabel(
            "Интервал: " + str(self.interval["interval_from"]) + ' - ' + str(self.interval["interval_to"]))
        layout.addWidget(new_interval_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_area.setWidget(scroll_container)
        scroll_layout = QVBoxLayout(scroll_container)

        photos = self.database_manager.get_all_photos_by_interval_id(self.interval["id"])
        for photo in photos:
            photo_button = FocusButton(photo["path"], scroll_container)
            # well_button.clicked.connect(lambda checked, name=button.text(): self.openProjectInterface(name))
            scroll_layout.addWidget(photo_button)
            photo_button.installEventFilter(self)
            photo_button.setStyleSheet("""
                                                QPushButton:focus { background-color: blue; color: white; }
                                            """)
            self.focusable_elements.append(photo_button)


class CreateIntervalWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, project, well, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.project = project
        self.well = well
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(
            lambda: self.switch_interface_callback(
                WellWidget,
                self.database_manager,
                self.project,
                self.well))

        project_name_label = QLabel(self.project["name"])
        layout.addWidget(project_name_label)

        well_name_label = QLabel(self.well["name"])
        layout.addWidget(well_name_label)

        new_interval_label = QLabel("Создание нового интервала")
        layout.addWidget(new_interval_label)

        # "Интервал От" виджет
        interval_from_widget = QWidget()
        interval_from_layout = CustomIntervalSpinBox(interval_from_widget, self)
        layout.addWidget(interval_from_widget)

        # "Интервал До" виджет
        interval_to_widget = QWidget()
        interval_to_layout = CustomIntervalSpinBox(interval_to_widget, self)
        layout.addWidget(interval_to_widget)

        # Кнопка сделать фотографии
        make_photo_button = FocusButton("Сделать фотографии")
        layout.addWidget(make_photo_button)
        make_photo_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        make_photo_button.installEventFilter(self)
        make_photo_button.clicked.connect(
            lambda: self.make_photo(interval_from_layout.spin_box.text(), interval_to_layout.spin_box.text()))

        self.focusable_elements.append(interval_from_layout.spin_box)
        self.focusable_elements.append(interval_to_layout.spin_box)
        self.focusable_elements.append(make_photo_button)

    def make_photo(self, interval_from, interval_to):
        photos = [os.path.join("photos", "photo_1.jpg"), os.path.join("photos", "photo_2.jpg")]
        self.switch_interface_callback(
            PhotoReviewWidget, self.database_manager, self.project, self.well, interval_from, interval_to, photos)



class WellWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, project, well, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.project = project
        self.well = well
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(
            lambda: self.switch_interface_callback(
                ProjectWidget,
                self.database_manager,
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
                self.project,
                self.well))
        self.focusable_elements.append(new_interval_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_area.setWidget(scroll_container)
        scroll_layout = QVBoxLayout(scroll_container)

        intervals = self.database_manager.get_all_intervals_by_well_id(self.well["id"])
        for interval in intervals:
            interval_button = FocusButton(str(interval["interval_from"]) + ' - ' + str(interval["interval_to"]),
                                          scroll_container)
            interval_button.clicked.connect(
                lambda: self.switch_interface_callback(IntervalWidget, self.database_manager, self.project, self.well,
                                                       interval)
            )
            scroll_layout.addWidget(interval_button)
            interval_button.installEventFilter(self)
            interval_button.setStyleSheet("""
                                                QPushButton:focus { background-color: blue; color: white; }
                                            """)
            self.focusable_elements.append(interval_button)


class CreateWellWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, project, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
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
        self.switch_interface_callback(WellWidget, self.database_manager, self.project, new_well)


class CreateProjectWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
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
            new_project,
            switch_interface_callback=self.switch_interface_callback,
            parent=None)


class ProjectWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, project, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.project = project
        self.switch_interface_callback = switch_interface_callback
        self.setup_ui()
        self.install_focus_event_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.create_back_button(
            lambda: self.switch_interface_callback(
                ChooseProjectWidget,
                self.database_manager))

        project_name_label = QLabel(self.project["name"])
        layout.addWidget(project_name_label)

        label = QLabel("Выбор скважины")
        layout.addWidget(label)

        new_well_button = FocusButton("Новая скважина")
        new_well_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        new_well_button.clicked.connect(
            lambda: self.switch_interface_callback(CreateWellWidget, self.database_manager, self.project)
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
                lambda: self.switch_interface_callback(WellWidget, self.database_manager, self.project, well)
            )
            scroll_layout.addWidget(well_button)
            well_button.setStyleSheet("""
                                        QPushButton:focus { background-color: blue; color: white; }
                                    """)
            self.focusable_elements.append(well_button)


class ChooseProjectWidget(BaseInterfaceWidget):
    def __init__(self, database_manager, switch_interface_callback, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
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
            lambda: self.switch_interface_callback(CreateProjectWidget, self.database_manager)
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
                lambda: self.switch_interface_callback(ProjectWidget, self.database_manager, project))
            scroll_layout.addWidget(project_button)
            project_button.setStyleSheet("""
                                QPushButton:focus { background-color: blue; color: white; }
                            """)
            self.focusable_elements.append(project_button)

        self.start_focus = new_project_button


class MainWindow(QMainWindow):
    def __init__(self, database_manager):
        super().__init__()
        self.setWindowTitle("GeoPhoto")

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создание и добавление главного интерфейса
        self.main_widget = ChooseProjectWidget(database_manager, self.switch_interface)
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
    if not os.path.exists(DATA_FOLDER_PATH):
        os.makedirs(DATA_FOLDER_PATH)

    db_manager = GeoPhotoDBManager()

    app = QApplication(sys.argv)
    window = MainWindow(db_manager)
    window.showFullScreen()

    app.aboutToQuit.connect(db_manager.close_connection)
    sys.exit(app.exec_())
