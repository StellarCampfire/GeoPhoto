from PyQt5.QtWidgets import (QMainWindow, QDoubleSpinBox)
from PyQt5.QtCore import Qt

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget


class BaseWindow(QMainWindow):
    def __init__(self, app_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app_instance
        self.start_focus = None
        self.focusable_elements = []

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

        return super().eventFilter(source, event)
