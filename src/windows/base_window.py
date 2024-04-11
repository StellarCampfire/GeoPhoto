from PyQt5.QtCore import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QScrollArea


class BaseWindow(QMainWindow):
    def __init__(self, app_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app_instance
        self.start_focus = None
        self.focusable_elements = []
        self.scroll_area = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

    def install_focus_event_filters(self):
        for element in self.focusable_elements:
            element.installEventFilter(self)

    def install_focusable_elements(self, *args):
        self.focusable_elements.clear()
        self.focusable_elements.extend(args)
        self.install_focus_event_filters()
        if len(self.focusable_elements) > 0:
            self.start_focus = self.focusable_elements[0]

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
            elif event.key() in [Qt.Key_Left, Qt.Key_Right]:
                if isinstance(source, QDoubleSpinBox):
                    pass
                else:
                    return True

        if event.type() == QEvent.FocusIn and self.scroll_area:
            self.scroll_area.ensureWidgetVisible(source)

        # Для всех остальных событий пропускаем обработку через базовый класс
        return super().eventFilter(source, event)

    def set_scroll_area(self, scroll_area):
        if isinstance(scroll_area, QScrollArea):
            self.scroll_area = scroll_area

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

    def get_config(self):
        return self.app.config_manager
