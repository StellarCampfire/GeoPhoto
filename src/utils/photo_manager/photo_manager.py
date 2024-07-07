import asyncio
import logging
import os
from src.utils.photo_manager.base_photo_manager import BasePhotoManager


class PhotoManager(BasePhotoManager):
    def __init__(self, temp_storage="temp/photos"):
        super().__init__(temp_storage)
        self.camera_indexes = [0, 1]  # indexes of cameras to be used

    # Asynchronously takes photos with both cameras set up
    async def take_photos(self, project, well, width=0, height=0):
        self.clear_temp_storage()
        tasks = []
        for camera_index in self.camera_indexes:
            photo_path = os.path.join(self.temp_photo_path,
                                      self.generate_unique_photo_name(project, well, camera_index))
            task = asyncio.create_task(take_photo_with_camera(camera_index, photo_path, width, height))
            tasks.append(task)
        return await asyncio.gather(*tasks)


# Asynchronously checks the number of available cameras by parsing the output of the command.
async def check_cameras():
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

        # Parsing the command output to determine the number of available cameras
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

def make_command(camera_index, photo_path, width=0, height=0):
    command = f"libcamera-still --nopreview"
    with open('./photo_command_parameters.txt') as file_command_parameters:
        lines = file_command_parameters.readlines()
        for line in lines:
            format_line = line.lstrip().replace("\r","").replace("\n","")
            if len(format_line) == 0 or format_line[0] == '#':
                continue
            command = command + " " + format_line

    if command.find(" --width ") == -1 and width != 0:
        command = command + f" --width {str(width)}"

    if command.find(" --height ") == -1 and width != 0:
        command = command + f" --height {str(height)}"

    if command.find(" --camera ") == -1:
        command = command + f" --camera {str(camera_index)}"

    if command.find(" -o ") == -1:
        command = command + f" -o {str(photo_path)}"

    print("photo command: " + command)
    return command


# Asynchronously executes the libcamera-still command to take a picture.
async def take_photo_with_camera(camera_index, photo_path, width=0, height=0):
    command = make_command(camera_index, photo_path, width, height)
    logging.info(f"Starting command {command}")
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    logging.info(f"Wait command result {command}")
    stdout, stderr = await process.communicate()

    stderr = stderr.decode('utf-8')
    if stderr:
        error_messages = [line for line in stderr.split('\n') if 'ERROR' in line or 'WARN' in line]
        if error_messages:
            logging.error(f"Error taking photo with camera {camera_index}: {stderr.decode()}")
            return None
    logging.info(f"Photo taken with camera {camera_index}: {photo_path}")
    return photo_path
