import os
import shutil
import logging
import json
from picamera2 import Picamera2
from libcamera import controls


class PhotoManager:
    def __init__(self):
        if not self.check_cameras():
            logging.error("At least 2 cameras are required for PhotoModule to work.")
            raise RuntimeError("At least 2 cameras are required for PhotoModule to work")

        self.first_camera = Picamera2(0)
        self.second_camera = Picamera2(1)

        config = self.first_camera.create_still_configuration()

        config["controls"]["AeEnable"] = False

        # Устанавливаем ручные настройки экспозиции
        config["controls"]["ExposureTime"] = 1000  # Выдержка в микросекундах, например, 1/50 секунды
        config["controls"]["AnalogueGain"] = 1.0

        # self.first_camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.0})
        # self.first_camera.set_controls({"LensPosition": 0.0})

        self.first_camera.configure(config)
        self.second_camera.configure(config)

        self.temp_photo_path = os.path.join("temp", "photos")
        if not os.path.exists(self.temp_photo_path):
            os.makedirs(self.temp_photo_path)

        self.permanent_storage_path = "permanent_storage"
        if not os.path.exists(self.permanent_storage_path):
            os.makedirs(self.permanent_storage_path)

        logging.info("PhotoModule started")

    def take_photos(self, project, well, interval_settings):
        return [
            self.take_photo_with_first_camera(project, well, interval_settings),
            self.take_photo_with_second_camera(project, well, interval_settings)]

    def take_photo_with_first_camera(self, project, well, interval_settings):
        photo_path = os.path.join(
            self.temp_photo_path, self.make_photo_name(project, well, interval_settings, 1))
        self.first_camera.start()
        self.first_camera.capture_file(photo_path)
        self.first_camera.stop()
        logging.info(f'Photo taken by first camera was saved in: {photo_path}')
        return photo_path

    def take_photo_with_second_camera(self, project, well, interval_settings):
        photo_path = os.path.join(
            self.temp_photo_path, self.make_photo_name(project, well, interval_settings, 2))
        self.second_camera.start()
        self.second_camera.capture_file(photo_path)
        self.second_camera.stop()
        logging.info(f'Photo taken by second camera was saved in: {photo_path}')
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

    def get_exposure_settins_value(self):
        min_exp, max_exp, default_exp = self.first_camera.camera_controls["ExposureTime"]
        logging.info(f'Camer exposure settins: min {min_exp}, max{max_exp}, default{default_exp}')

    def set_controls(self, exp, iso, lens_position):
        self.first_camera.set_controls({"ExposureTime": exp, "AnalogueGain": iso})
        self.second_camera.set_controls({"ExposureTime": exp, "AnalogueGain": iso})

    def set_controls_and_take_photo(self, project, well, interval_settings, exp, iso, lens_position):
        self.set_controls(exp, iso, lens_position)
        return self.take_photo_with_first_camera(project, well, interval_settings)

    @staticmethod
    def make_photo_name(project, well, interval_settings, photo_num):
        photo_name = (f'{project.name}_{well.name}_{interval_settings.interval_from}_'
                      f'{interval_settings.interval_to}_{str(interval_settings.is_marked)}_'
                      f'{interval_settings.condition.name}_photo{str(photo_num)}.jpg')
        return photo_name

    @staticmethod
    def check_cameras():
        camera_info = Picamera2.global_camera_info()
        str_camera_info = "\n".join(json.dumps(camera, indent=2) for camera in camera_info)
        logging.info(f'CAMERAS INFO: \n{str_camera_info}')
        return len(camera_info) >= 2
