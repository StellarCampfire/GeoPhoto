from src.views.BaseWindow import BaseWindow
from src.views.IntervalWindow import IntervalWindow
from src.views.NewIntervalWindow import NewIntervalWindow
from resources.py.PhotoReviewForm import Ui_PhotoReviewForm

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


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