import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QScrollArea, QMainWindow, QLabel, QStackedWidget, QLineEdit)
from PyQt5.QtCore import Qt, QEvent

class FocusButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if isinstance(self.parent(), QWidget):
            scroll_area = self.findParentScrollArea(self.parent())
            if scroll_area:
                scroll_area.ensureWidgetVisible(self)

    @staticmethod
    def findParentScrollArea(widget):
        parent = widget.parent()
        while parent is not None:
            if isinstance(parent, QScrollArea):
                return parent
            parent = parent.parent()
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoPhoto")

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.buttons = []

        # Создание и добавление главного интерфейса
        self.main_widget = QWidget()
        self.setupMainInterface()
        self.stacked_widget.addWidget(self.main_widget)

        # Создание и добавление интерфейса "Новый проект"
        self.new_project_widget = self.createNewProjectInterface()
        self.stacked_widget.addWidget(self.new_project_widget)

    def setupMainInterface(self):
        layout = QVBoxLayout(self.main_widget)

        project_selection_label = QLabel("Выбор проекта")
        layout.addWidget(project_selection_label)

        new_project_button = FocusButton("Новый проект")
        layout.addWidget(new_project_button)
        new_project_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        new_project_button.installEventFilter(self)
        new_project_button.clicked.connect(self.openNewProjectInterface)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_area.setWidget(scroll_container)
        scroll_layout = QVBoxLayout(scroll_container)

        self.buttons = [new_project_button]
        for i in range(40):
            button = FocusButton(f'Button {i + 1}', scroll_container)
            button.clicked.connect(lambda checked, name=button.text(): self.openProjectInterface(name))
            scroll_layout.addWidget(button)
            button.installEventFilter(self)
            button.setStyleSheet("""
                        QPushButton:focus { background-color: blue; color: white; }
                    """)
            self.buttons.append(button)

        new_project_button.setFocus()

    def openNewProjectInterface(self):
        new_project_widget = self.createNewProjectInterface()
        self.stacked_widget.addWidget(new_project_widget)
        self.stacked_widget.setCurrentWidget(new_project_widget)


    def openProjectInterface(self, project_name):
        project_widget = self.createProjectInterface(project_name)
        self.stacked_widget.addWidget(project_widget)
        self.stacked_widget.setCurrentWidget(project_widget)

    def createNewProjectInterface(self):
        new_project_widget = QWidget()
        layout = QVBoxLayout(new_project_widget)

        # Метка "Создание нового проекта"
        create_project_label = QLabel("Новый проект")
        layout.addWidget(create_project_label)

        # Поле ввода "Название проекта"
        project_name_input = QLineEdit()
        project_name_input.setPlaceholderText("Название проекта")
        layout.addWidget(project_name_input)

        # Кнопка "Создать"
        create_button = QPushButton("Создать")
        layout.addWidget(create_button)

        # Здесь можно добавить обработчик нажатия кнопки "Создать"
        # Например, сохранение названия проекта и переход к интерфейсу проекта
        create_button.clicked.connect(lambda: self.createNewProject(project_name_input.text()))

        return new_project_widget


    def createProjectInterface(self, project_name):
        project_widget = QWidget()
        layout = QVBoxLayout(project_widget)
        project_name_label = QLabel(project_name)
        layout.addWidget(project_name_label)

        label = QLabel("Выбор скважины")
        layout.addWidget(label)

        new_well_button = FocusButton("Новая скважина")
        layout.addWidget(new_well_button)
        new_well_button.setStyleSheet("QPushButton:focus { background-color: blue; color: white; }")
        new_well_button.installEventFilter(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_area.setWidget(scroll_container)
        scroll_layout = QVBoxLayout(scroll_container)

        self.buttons = [new_well_button]
        for i in range(40):
            button = FocusButton(f'Button {i + 1}', scroll_container)
            # button.clicked.connect(lambda checked, name=button.text(): self.openProjectInterface(name))
            scroll_layout.addWidget(button)
            button.installEventFilter(self)
            button.setStyleSheet("""
                                QPushButton:focus { background-color: blue; color: white; }
                            """)
            self.buttons.append(button)

        new_well_button.setFocus()

        return project_widget

    def openNewProjectInterface(self):
        self.stacked_widget.setCurrentWidget(self.new_project_widget)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source in self.buttons:
            print(event)
            print(source)
            idx = self.buttons.index(source)
            if event.key() == Qt.Key_Up:
                if idx > 0:
                    self.buttons[idx - 1].setFocus()
                else:
                    self.buttons[-1].setFocus()  # Переход к последней кнопке, если фокус на первой
                return True
            elif event.key() == Qt.Key_Down:
                if idx < len(self.buttons) - 1:
                    self.buttons[idx + 1].setFocus()
                else:
                    self.buttons[0].setFocus()  # Переход к первой кнопке, если фокус на последней
                return True

        return super().eventFilter(source, event)

    def createNewProject(self, project_name):
        print(project_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
