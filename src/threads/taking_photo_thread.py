from PyQt5.QtCore import QThread, pyqtSignal


class PhotoTakingThread(QThread):
    photos_ready = pyqtSignal(list)  # Сигнал для отправки списка путей к фотографиям

    def __init__(self, photo_manager, project, well):
        super().__init__()
        self.photo_manager = photo_manager
        self.project = project
        self.well = well

    def run(self):
        photos = self.photo_manager.take_photos(self.project, self.well)
        self.photos_ready.emit(photos)  # Отправка фотографий обратно в основной поток
