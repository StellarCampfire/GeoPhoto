import os
import shutil
import random
import logging
import asyncio
from src.utils.photo_manager.base_photo_manager import BasePhotoManager


class PhotoManagerEmulator(BasePhotoManager):
    def __init__(
            self,
            temp_storage=os.path.join("temp", "photos"),
            sample_images_dir=os.path.join("resources", "img", "sample_images")):
        super().__init__(temp_storage)
        self.sample_images_dir = sample_images_dir
        self.ensure_sample_images()

    # Ensure the sample images directory exists and has images.
    def ensure_sample_images(self):
        os.makedirs(self.sample_images_dir, exist_ok=True)
        if not os.listdir(self.sample_images_dir):
            logging.warning("No sample images found in %s. Please add some JPEG files to use as samples.",
                            self.sample_images_dir)

    # Imitates capturing a photo using a sample image instead of a real camera.
    async def take_photo_with_camera(self, project, well, camera_num):
        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate delay
        sample_image_path = self.choose_sample_image()
        if not sample_image_path:
            logging.error("No sample image available to simulate photo capture.")
            return None

        photo_name = self.generate_unique_photo_name(project, well, camera_num)
        photo_path = os.path.join(self.temp_photo_path, photo_name)
        shutil.copy(sample_image_path, photo_path)
        logging.info("Simulated photo taken and saved at %s using %s", photo_path, sample_image_path)
        return photo_path

    # Randomly selects a sample image from the sample directory.
    def choose_sample_image(self):
        try:
            return random.choice([
                os.path.join(self.sample_images_dir, f)
                for f in os.listdir(self.sample_images_dir)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ])
        except IndexError:
            return None

    # Simulates capturing photos using both configured cameras asynchronously.
    async def take_photos(self, project, well, width=0, height=0):
        self.clear_temp_storage()
        tasks = [
            self.take_photo_with_camera(project, well, 1),
            self.take_photo_with_camera(project, well, 2)
        ]
        return await asyncio.gather(*tasks)
