import os
import logging
import shutil
import time
import uuid
from abc import ABC, abstractmethod


class BasePhotoManager(ABC):
    def __init__(self, temp_storage="temp/photos"):
        self.temp_photo_path = temp_storage
        self.permanent_storage_path_in_project = 'media'
        self.setup_default_command_parameters()
        self.setup_paths()

    @abstractmethod
    def take_photos(self, project, well, width=0, height=0):
        """Captures photos using both configured cameras."""

    def setup_default_command_parameters(self):
        file_path = "./photo_command_parameters.txt"

        if not os.path.exists(file_path):
            with open(file_path, "w", encoding='utf-8') as command_file:
                command_file.writelines(
                    [
                        "# A comment line starts with symbol '#'\n",
                        "# the default command is \"libcamera-still --nopreview\"\n",
                        "# you can add and change any another parameters\n",
                        "--autofocus-mode manual\n",
                        "--lens-position 5\n",
                        "--metering spot\n",
                    ]
                )

    def setup_paths(self):
        """Ensure all required directories exist."""
        os.makedirs(self.temp_photo_path, exist_ok=True)
        logging.info("Storage paths set up at %s.", self.temp_photo_path)

    def move_photos(self, destination, interval):
        """Moves and renames all photos from the temporary location to the specified destination."""
        moved_photos = []
        for filename in os.listdir(self.temp_photo_path):
            src = os.path.join(self.temp_photo_path, filename)
            # Decompose the filename to insert interval name
            parts = filename.split("_")
            # Assuming filename format is "ProjectName_WellName_cameraX_timestamp_uuid.jpg"
            new_filename_parts = parts[:2]  # ProjectName and WellName
            new_filename_parts.append(interval.get_full_name())  # Add interval full name
            new_filename_parts.extend(parts[2:3])  # cameraX, timestamp, uuid, and .jpg
            new_filename = "_".join(new_filename_parts)
            new_filename = new_filename + ".jpg"
            dest = os.path.join(destination, new_filename)
            shutil.move(src, dest)
            moved_photos.append(dest)
            logging.info("Photo moved and renamed to %s", dest)
        return moved_photos

    def clear_temp_storage(self):
        """Clears all files in the temporary storage directory."""
        for filename in os.listdir(self.temp_photo_path):
            file_path = os.path.join(self.temp_photo_path, filename)
            os.remove(file_path)
            logging.info("Cleared temporary file %s", file_path)

    def save_photos_to_permanent_storage(self, project, well, interval):
        """Moves photos from temporary to permanent storage, renaming them to include interval details."""
        permanent_folder = os.path.join(
            project.path,
            self.permanent_storage_path_in_project,
            project.name,
            well.name)
        os.makedirs(permanent_folder, exist_ok=True)
        return self.move_photos(permanent_folder, interval)

    @staticmethod
    def generate_unique_photo_name(project, well, camera_num):
        """Generates a unique photo name using timestamp and UUID."""
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex
        return f"{project.name}_{well.name}_camera{camera_num}_{timestamp}_{unique_id}.jpg"
