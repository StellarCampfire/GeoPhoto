import os
import logging
import threading
import gc
import time

from PyQt5.QtCore import QThread, pyqtSignal

from src.utils.photo_manager.base_photo_manager import BasePhotoManager

from picamera2 import Picamera2


class CameraThread(QThread):
    photoTaken = pyqtSignal(str, name='photoTaken')

    def __init__(self, camera_index, photo_path):
        super().__init__()
        self.camera_index = camera_index
        self.photo_path = photo_path

    def run(self):
        try:
            camera = Picamera2(self.camera_index)
            config = camera.create_still_configuration()
            camera.configure(config)
            camera.start()
            camera.capture_file(self.photo_path)
            camera.stop()
            camera.close()
            self.photoTaken.emit(self.photo_path)
        except Exception as e:
            logging.error(f"Error capturing photo with camera {self.camera_index}: {e}")
        finally:
            self.cleanup()

        def cleanup(self):
            print("Cleaning up the thread and camera resources.")
            self.deleteLater()


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
        self.camera_indexes = [0, 1]

    def take_photo_with_camera_and_free_mem(self, camera_index, photo_path):
        logging.debug(f'take_photo_with_camera_and_free_mem {camera_index}: starting ctx ...')
        with CameraContextManager(camera_index) as camera:
            logging.debug(f'take_photo_with_camera_and_free_mem {camera_index}: ctx started')
            camera.capture_file(photo_path)

        logging.debug(f'take_photo_with_camera_and_free_mem {camera_index}: ctx closed.')
        gc.collect()
        logging.debug(f'take_photo_with_camera_and_free_mem {camera_index}: gc collected.')
        return photo_path

    def take_photos(self, project, well):
        """Initiates photo capture on all cameras in separate threads."""
        logging.debug("take_photos: Starting taking photo process ..... ")
        result = []
        for camera_index in self.camera_indexes:
            photo_path = os.path.join(self.temp_photo_path,
                                      self.generate_unique_photo_name(project, well, camera_index))
            logging.debug(f'take_photos: start take_photo_camera_and_free_mem for camera {camera_index}')
            photo_result = self.take_photo_with_camera_and_free_mem(camera_index, photo_path)
            logging.debug(f'take_photos: finish take_photo_camera_and_free_mem for camera {camera_index}')
            result.append(photo_result)
            logging.debug(f'take_photos {camera_index}: sleeping...')
            time.sleep(4)
            logging.debug(f'take_photos {camera_index}: wake up...')

        return result

    @staticmethod
    def generate_unique_photo_name(project, well, camera_num):
        import time, uuid
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex
        return f"{project.name}_{well.name}_camera{camera_num}_{timestamp}_{unique_id}.jpg"

    def cleanup_and_proceed(self):
        sender_thread = self.sender()
        if sender_thread:
            sender_thread.deleteLater()
        gc.collect()  # Call garbage collection
        # Here you can start the next operation or camera thread
        if sender_thread.camera_index == 0:
            self.take_photo(1)

    @staticmethod
    def check_cameras():
        """Checks if at least two cameras are available."""
        camera_info = Picamera2.global_camera_info()
        if len(camera_info) < 2:
            logging.error("Insufficient cameras available; at least 2 are required.")
            return False
        logging.info("Camera availability confirmed.")
        return True


