from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from src.windows.base_window import BaseWindow
from src.core.window_types import WindowType
from resources.py.PhotoReviewForm import Ui_PhotoReviewForm


class PhotoReviewWindow(BaseWindow):
    def __init__(self, project, well, interval_settings, app_instance, parent=None):
        super().__init__(app_instance, parent)

        self.project = project
        self.well = well
        self.interval_settings = interval_settings

        self.photos = None
        self.current_photo_index = None

        self.ui = Ui_PhotoReviewForm()
        self.ui.setupUi(self.central_widget)

        self.ui.yes_pushButton.clicked.connect(self.on_yes_clicked)
        self.ui.no_pushButton.clicked.connect(self.on_no_clicked)

        self.photos = self.get_photo_manager().take_photos(self.project, self.well)
        # # Инициализация потока и подключение сигналов
        # self.photo_thread = PhotoTakingThread(self.get_photo_manager(), project, well)
        # self.photo_thread.photos_ready.connect(self.update_photos)
        # self.photo_thread.start()  # Запуск потока

        # Показать сообщение о загрузке
        self.ui.photo_label.setText("Загрузка фотографий...")

        # Focus
        self.install_focusable_elements(
            self.ui.yes_pushButton,
            self.ui.no_pushButton)

        self.start_focus = self.ui.yes_pushButton


    def update_photos(self, photos):
        self.photos = photos
        self.current_photo_index = 0
        if self.photos:
            self.load_image()
        else:
            self.ui.photo_label.setText("Фотографии не найдены.")

    def on_yes_clicked(self):
        if self.current_photo_index < len(self.photos) - 1:
            self.current_photo_index += 1
            self.load_image()
        else:
            new_interval_id = self.get_database_manager().add_interval(self.well.id, self.interval_settings)
            new_interval = self.get_database_manager().get_interval(new_interval_id)

            permanent_photo_paths = self.get_photo_manager().save_photos_to_permanent_storage(
                self.project,
                self.well,
                new_interval)

            for path in permanent_photo_paths:
                self.get_database_manager().add_photo(path, new_interval.id)

            self.goto_interval(new_interval)

    def on_no_clicked(self):
        self.get_photo_manager().clear_temp_storage()
        self.goto_new_interval()

    def load_image(self):
        if self.photos:
            pixmap = QPixmap(self.photos[self.current_photo_index])
            scaled_pixmap = pixmap.scaled(self.ui.photo_label.size(), Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)
            self.ui.photo_label.setPixmap(scaled_pixmap)

    # def showEvent(self, event):
    #     super().showEvent(event)
    #     self.load_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'ui'):
            self.load_image()

    def goto_interval(self, interval):
        self.switch_interface(WindowType.INTERVAL_WINDOW, self.project, self.well, interval)

    def goto_new_interval(self):
        self.switch_interface(WindowType.NEW_INTERVAL_WINDOW, self.project, self.well, self.interval_settings)
