import os
import shutil
import logging


class PhotoManagerEmulator:
    def __init__(self):
        self.temp_photo_path = os.path.join("temp", "photos")
        if not os.path.exists(self.temp_photo_path):
            os.makedirs(self.temp_photo_path)

        self.permanent_storage_path = "permanent_storage"
        if not os.path.exists(self.permanent_storage_path):
            os.makedirs(self.permanent_storage_path)

        logging.info("PhotoModuleEmulator started")

    def take_photos(self, project, well, interval_settings):
        return [
            self.take_photo_with_first_camera(project, well, interval_settings),
            self.take_photo_with_second_camera(project, well, interval_settings)]

    def take_photo_with_first_camera(self, project, well, interval_settings):
        photo_path = os.path.join(
            self.temp_photo_path, self.make_photo_name(project, well, interval_settings, 1))

        shutil.copy(os.path.join("photos", "photo_1.jpg"), photo_path)
        logging.info(f'Photo taken by first camera EMULATOR was saved in: {photo_path}')
        return photo_path

    def take_photo_with_second_camera(self, project, well, interval_settings):
        photo_path = os.path.join(
            self.temp_photo_path, self.make_photo_name(project, well, interval_settings, 2))
        shutil.copy(os.path.join("photos", "photo_2.jpg"), photo_path)
        logging.info(f'Photo taken by second camera EMULATOR was saved in: {photo_path}')
        return photo_path

    def save_photos_to_permanent_storage(self, project, well, interval_settings):
        if not os.path.exists(self.temp_photo_path):
            logging.info("Temporary photo storage does not exist.")
            return

        interval_folder_name = (f'{interval_settings.interval_from}_'
                                f'{interval_settings.interval_to}_'
                                f'{"Marked" if interval_settings.is_marked else "NotMarked"}_'
                                f'{interval_settings.condition.name}')
        permanent_folder_path = os.path.join(self.permanent_storage_path,
                                             project.name,
                                             well.name,
                                             interval_folder_name)

        # Create path if not exists
        if not os.path.exists(permanent_folder_path):
            os.makedirs(permanent_folder_path)

        # Move photos
        permanent_photos = []
        for filename in os.listdir(self.temp_photo_path):
            temp_file_path = os.path.join(self.temp_photo_path, filename)
            permanent_file_path = os.path.join(permanent_folder_path, filename)
            shutil.move(temp_file_path, permanent_file_path)
            permanent_photos.append(permanent_file_path)

        photos_paths = "\n".join(permanent_photos)
        logging.info(f"All photos moved to permanent storage:\n{photos_paths}")

        return permanent_photos

    def _save_photos_to_permanent_storage(self):
        if not os.path.exists(self.temp_photo_path):
            logging.info("Temporary photo storage does not exist.")
            return

        for filename in os.listdir(self.temp_photo_path):
            temp_file_path = os.path.join(self.temp_photo_path, filename)
            permanent_file_path = os.path.join(self.permanent_storage_path, filename)
            shutil.move(temp_file_path, permanent_file_path)

        logging.info("All photos moved to permanent storage.")

    def clear_temp_storage(self):
        if not os.path.exists(self.temp_photo_path):
            logging.info("Temporary photo storage does not exist.")
            return

        for filename in os.listdir(self.temp_photo_path):
            file_path = os.path.join(self.temp_photo_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    logging.info(f"File {file_path} was removed from temporary storage.")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    logging.info(f"Directory {file_path} was removed from temporary storage.")
            except Exception as e:
                logging.error(f"Failed to delete {file_path}. Reason: {e}")


    @staticmethod
    def make_photo_name(project, well, interval_settings, photo_num):
        photo_name = (f'{project.name}_{well.name}_{interval_settings.interval_from}_'
                      f'{interval_settings.interval_to}_{str(interval_settings.is_marked)}_'
                      f'{interval_settings.condition.name}_photo{str(photo_num)}.jpg')
        return photo_name

