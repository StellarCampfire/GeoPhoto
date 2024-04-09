import os
import logging
import threading

from src.utils.photo_manager.base_photo_manager import BasePhotoManager
from picamera2 import Picamera2


class PhotoManager(BasePhotoManager):
    def __init__(self, temp_storage="temp/photos", permanent_storage="permanent_storage"):
        super().__init__(temp_storage, permanent_storage)
        self.cameras = []
        if self.check_cameras():
            self.setup_cameras()

    def setup_cameras(self):
        """Initializes cameras with configurations."""
        try:
            # Create and configure cameras
            self.cameras = [Picamera2(i) for i in range(2)]
            config = self.cameras[0].create_still_configuration()
            for camera in self.cameras:
                camera.configure(config)
            logging.info("Cameras configured successfully.")
        except Exception as e:
            logging.error(f"Camera setup failed: {e}")
            raise

    def take_photo_with_camera(self, camera, project, well, camera_num):
        """Captures a photo using the specified camera."""
        photo_name = self.generate_unique_photo_name(project, well, camera_num)
        photo_path = os.path.join(self.temp_photo_path, photo_name)
        try:
            camera.start()
            camera.capture_file(photo_path)
            camera.stop()
            logging.info(f"Photo captured and saved at {photo_path}")
            return photo_path
        except Exception as e:
            logging.error(f"Failed to capture photo with camera {camera_num}: {e}")
            return None

    def take_photos(self, project, well):
        """Initiates photo capture on all cameras in separate threads."""
        threads = []
        results = [None] * len(self.cameras)

        def capture(index, camera):
            results[index] = self.take_photo_with_camera(camera, project, well, index + 1)

        for i, camera in enumerate(self.cameras):
            thread = threading.Thread(target=capture, args=(i, camera))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()  # Wait for all threads to complete

        return results

    @staticmethod
    def check_cameras():
        """Checks if at least two cameras are available."""
        camera_info = Picamera2.global_camera_info()
        if len(camera_info) < 2:
            logging.error("Insufficient cameras available; at least 2 are required.")
            return False
        logging.info("Camera availability confirmed.")
        return True

    @staticmethod
    def generate_unique_photo_name(project, well, camera_num):
        """Generates a unique photo name based on project, well, and camera number."""
        import time, uuid
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex
        return f"{project.name}_{well.name}_camera{camera_num}_{timestamp}_{unique_id}.jpg"
