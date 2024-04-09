import os
import logging

from src.utils.photo_manager.base_photo_manager import BasePhotoManager

from picamera2 import Picamera2
from libcamera import controls


class PhotoManager(BasePhotoManager):
    def __init__(self, temp_storage="temp/photos", permanent_storage="permanent_storage"):
        super().__init__(temp_storage, permanent_storage)
        self.temp_photo_path = temp_storage
        self.permanent_storage_path = permanent_storage
        self.cameras = []
        self.check_cameras()  # Ensures cameras are available before proceeding
        self.setup_cameras()

    def setup_cameras(self):
        """Initializes cameras with configurations."""
        try:
            self.cameras.append(Picamera2(0))
            self.cameras.append(Picamera2(1))
            config = self.cameras[0].create_still_configuration()
            for camera in self.cameras:
                camera.configure(config)
            logging.info("Cameras configured successfully.")
        except Exception as e:
            logging.error("Camera setup failed: %s", e)
            raise

    def take_photo_with_camera(self, camera, project, well, camera_num):
        """General method to capture a photo using a specified camera."""
        photo_name = self.generate_unique_photo_name(project, well, camera_num)
        photo_path = os.path.join(self.temp_photo_path, photo_name)
        try:
            camera.start()
            camera.capture_file(photo_path)
            camera.stop()
            logging.info("Photo captured and saved at %s", photo_path)
            return photo_path
        except Exception as e:
            logging.error("Failed to capture photo with camera %d: %s", camera_num, e)
            return None

    def take_photos(self, project, well):
        """Captures photos using both configured cameras."""
        self.clear_temp_storage()
        return [self.take_photo_with_camera(camera, project, well, index)
                for index, camera in enumerate(self.cameras, start=1)]

    @staticmethod
    def check_cameras():
        """Checks that sufficient cameras are available."""
        camera_info = Picamera2.global_camera_info()
        if len(camera_info) < 2:
            logging.error("Insufficient cameras available; at least 2 are required.")
            raise RuntimeError("Insufficient cameras available.")
        logging.info("Camera availability confirmed.")
