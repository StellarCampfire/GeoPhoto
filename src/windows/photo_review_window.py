import asyncio
import logging
import os.path

from PIL import Image

from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QMovie

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
        self.current_photo_index = 0

        self.ui = Ui_PhotoReviewForm()
        self.ui.setupUi(self.central_widget)

        self.ui.yes_pushButton.clicked.connect(self.on_yes_clicked)
        self.ui.no_pushButton.clicked.connect(self.on_no_clicked)

        self.photo_thread = PhotoThread(
            self.get_photo_manager(),
            project,
            well,
            self.get_config().get('camera', 'width', fallback=0),
            self.get_config().get('camera', 'height', fallback=0))
        self.photo_thread.photos_ready.connect(self.update_photos)
        self.photo_thread.start()

        # Блокировка кнопок
        self.ui.yes_pushButton.setEnabled(False)
        self.ui.no_pushButton.setEnabled(False)

        # Показать анимацию загрузки
        self.loading_movie = QMovie(os.path.join("resources", "animations", "loading.gif"))
        self.ui.photo_label.setMovie(self.loading_movie)
        self.loading_movie.start()

        # Focus
        self.install_focusable_elements(
            self.ui.yes_pushButton,
            self.ui.no_pushButton)

        self.start_focus = self.ui.yes_pushButton

    @pyqtSlot(list)
    def update_photos(self, photos):
        self.photos = photos
        self.current_photo_index = 0
        if self.photos:
            for photo in self.photos:
                try:
                    crop_image(
                        photo,
                        int(self.get_config().get("crop", "left", fallback=0)),
                        int(self.get_config().get("crop", "right", fallback=0)),
                        int(self.get_config().get("crop", "top", fallback=0)),
                        int(self.get_config().get("crop", "bottom", fallback=0)))
                except Exception as e:
                    self.ui.photo_label.setText(f"Ошибка при обработке фото: {str(e)}")
                    self.ui.no_pushButton.setEnabled(True)
                    self.ui.no_pushButton.setFocus()
                    return
            self.load_image()
            self.ui.yes_pushButton.setEnabled(True)
            self.ui.yes_pushButton.setFocus()
            self.ui.no_pushButton.setEnabled(True)
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


class PhotoThread(QThread):
    photos_ready = pyqtSignal(list)

    def __init__(self, photo_manager, project, well, width, height, parent=None):
        super().__init__(parent)
        self.photo_manager = photo_manager
        self.project = project
        self.well = well
        self.width = width
        self.height = height

    def run(self):
        """Запускает event loop asyncio и получает фотографии асинхронно."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        photos = loop.run_until_complete(self.photo_manager.take_photos(self.project, self.well, self.height))
        loop.close()
        self.photos_ready.emit(photos)


def crop_image(file_path, left, right, top, bottom):
    try:
        with Image.open(file_path) as img:
            width, height = img.size

            crop_area = (left, top, width - right, height - bottom)
            cropped_img = img.crop(crop_area)
            cropped_img.save(file_path, quality=95)
    except Exception as e:
        logging.error(f"Error while cropp {file_path}: {str(e)}")
        raise

