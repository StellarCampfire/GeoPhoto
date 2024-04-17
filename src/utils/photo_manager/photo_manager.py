import asyncio
import logging
import os
from src.utils.photo_manager.base_photo_manager import BasePhotoManager


class PhotoManager(BasePhotoManager):
    def __init__(self, temp_storage="temp/photos"):
        super().__init__(temp_storage)
        self.camera_indexes = [0, 1]  # индексы камер, которые будут использоваться

    async def take_photo_with_camera(self, camera_index, photo_path):
        """Асинхронно выполняет команду libcamera-still для съемки фотографии."""
        command = f"libcamera-still --camera {camera_index} --nopreview -o {photo_path}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if stderr:
            logging.error(f"Error taking photo with camera {camera_index}: {stderr.decode()}")
            return None
        logging.info(f"Photo taken with camera {camera_index}: {photo_path}")
        return photo_path

    async def take_photos(self, project, well):
        """Асинхронно фотографирует с обеих настроенных камер."""
        tasks = []
        for camera_index in self.camera_indexes:
            photo_path = os.path.join(self.temp_photo_path,
                                      self.generate_unique_photo_name(project, well, camera_index))
            task = asyncio.create_task(self.take_photo_with_camera(camera_index, photo_path))
            tasks.append(task)
        return await asyncio.gather(*tasks)

    @staticmethod
    async def check_cameras(self):
        """Асинхронно проверяет количество доступных камер, парся вывод команды."""
        command = "libcamera-hello --list-cameras"
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if stderr:
                logging.error(f"Error checking cameras: {stderr.decode()}")
                return False

            # Парсинг вывода команды для определения количества доступных камер
            num_cameras = sum(1 for line in stdout.decode().split('\n') if
                              line.strip().startswith(tuple(f"{i} :" for i in range(10))))
            if num_cameras >= 2:
                logging.info(f"Camera availability confirmed. Number of cameras: {num_cameras}")
                return True
            else:
                logging.error(f"Insufficient cameras available; at least 2 are required. Only {num_cameras} found.")
                return False
        except Exception as e:
            logging.error(f"An error occurred while checking cameras: {e}")
            return False
