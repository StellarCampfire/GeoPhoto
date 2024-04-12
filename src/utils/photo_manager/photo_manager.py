import os
import logging
import threading
import gc
import time

from threading import Event

from PyQt5.QtCore import QThread, pyqtSignal

from src.utils.photo_manager.base_photo_manager import BasePhotoManager

from picamera2 import Picamera2

class CameraContextManager:
    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.camera = None

    def __enter__(self):
        self.camera = Picamera2(self.camera_index)
        config = self.camera.create_still_configuration()
        self.camera.configure(config)
        logging.debug(f'CameraContextManager {self.camera_index}: starting camera...')
        self.camera.start()
        logging.debug(f'CameraContextManager {self.camera_index}: camera started.')
        return self.camera

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug(f'CameraContextManager {self.camera_index}: stoping camera...')
        self.camera.stop()
        logging.debug(f'CameraContextManager {self.camera_index}: camera stoped.')
        del self.camera
        logging.debug(f'CameraContextManager {self.camera_index}: camera deleted.')
        gc.collect()
        logging.debug(f'CameraContextManager {self.camera_index}: gc collected.')

class PhotoManager(BasePhotoManager):
    def __init__(self, temp_storage="temp/photos"):
        super().__init__(temp_storage)
        self.ready_to_start_next = Event()
        self.ready_to_start_next.set()  # Изначально разрешаем стартовать первой камере

    def take_photo_with_camera(self, camera_index, photo_path):
        self.ready_to_start_next.wait()  # Ждем разрешения на старт
        self.ready_to_start_next.clear()  # Сбрасываем событие для блокировки следующей камеры
        with CameraContextManager(camera_index) as camera:
            camera.capture_file(photo_path)
        self.ready_to_start_next.set()  # Разрешаем следующей камере начать работу
        gc.collect()  # Принудительная сборка мусора
        return photo_path

    def take_photos(self, project, well):
        result = []
        for camera_index in self.camera_indexes:
            photo_path = os.path.join(self.temp_photo_path,
                                      self.generate_unique_photo_name(project, well, camera_index))
            photo_result = self.take_photo_with_camera(camera_index, photo_path)
            result.append(photo_result)
        return result
    @staticmethod
    def check_cameras():
        """Checks if at least two cameras are available."""
        camera_info = Picamera2.global_camera_info()
        if len(camera_info) < 2:
            logging.error("Insufficient cameras available; at least 2 are required.")
            return False
        logging.info("Camera availability confirmed.")
        return True


