import os

from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtWidgets import QWidget

class CustomSpinBox(QWidget):
    def __init__(self, spin_box, decrease_button, increase_button, parent=None):
        super().__init__(parent)

        self.style = self.load_styles_from_file(os.path.join('resources', 'styles', 'style.qss'))

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

    def load_styles_from_file(self, file_path):
        with open(file_path, "r", encoding='utf-8') as file:
            return file.read()