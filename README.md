# GeoPhoto Documentation

## Overview

GeoPhoto is a software solution designed to be installed on a Raspberry Pi equipped with two attached cameras. The system is specifically engineered to traverse a geological core, capturing images at 0.5-meter intervals using both cameras. This setup is typically mounted on a specialized device that facilitates precise movement along the core samples.

## Features

- **Project Management:** Users can create projects within the software, each containing multiple wells. Each well can have numerous defined intervals, and each interval stores two photographs taken from the two different cameras.
- **Photo Storage:** All photographs are stored within the project's `media` folder, organizing data efficiently and simplifying access to visual information.
- **Photo Review and Confirmation:** After photographs are taken, the operator has the option to confirm each image sequentially. If an image is deemed unsatisfactory, the operator can revert to the interval editing stage for retakes or adjustments.
- **Customizable Photo Resolution and Processing:** Users can adjust the resolution of the photographs and set parameters for how much can be trimmed from each side of an image to reduce file size and optimize storage.

## Technical Details

- **Programming Language:** Python
- **Key Libraries Used:**
  - `PyQt5` for the graphical user interface
  - `logging` for operational logging
  - `sqlite3` for local database management
  - `ConfigParser` for configuration management
  - `PIL` for image processing
  - `pyinstaller` for compiling the project into an executable file
- **Configuration and Logs:** The application generates a `config.ini` file and maintains a `logs` directory to record operational logs, enhancing troubleshooting and maintenance.

## Building the Project

The software can be built for both Windows and Linux operating systems using the provided build script. To build the application, use one of the following commands depending on your operating system:

- **For Windows:**
  ```bash
  python build_project.py --os windows --ui
  ```

- **For Linux:**
  ```bash
  python build_project.py --os linux --ui
  ```

These commands will compile the project, incorporating all necessary user interface elements.

## Entry Point and Distribution

- **Main Entry Point:** `main.py`
- **Executable Output:** The compiled application, `GeoPhoto.exe`, can be found in the `dist` directory following successful compilation.
- **Project Structure:** Each project is self-contained within its own directory, which includes a `.json` file for project metadata, a `.db` file for the database, and a `media` folder for storing images.

This structure ensures that each project is portable and encapsulated, 
making management and archival straightforward.

## Usage and Deployment

Deploying GeoPhoto on a Raspberry Pi involves setting up the hardware with the two cameras, 
installing the software, and configuring the device for field deployment. 
The user-friendly interface allows geologists and technicians to efficiently 
manage geological core imaging tasks directly from the field.

## Running the Application

You can run the GeoPhoto application directly from the command line using Python. This method is especially useful for development, testing, or when you need to run the application on systems without the compiled executable. Below are the details on how to launch the application with various runtime options:

### Command Line Arguments

- **`--resolution`**: Sets the resolution of the application window. For example, `--resolution 1280x720` will set the window size to 1280 by 720 pixels. If this argument is not provided, the application will run in fullscreen mode.
- **`--log-level`**: Specifies the verbosity level of the application logs. Available options are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. Setting this to `DEBUG` will capture detailed logs that are helpful during development.
- **`--emulate`**: Enables the camera emulation mode. This mode uses predefined images instead of capturing real photos from the cameras. This is particularly useful for running the application on devices without attached cameras, allowing developers and testers to simulate camera input.

### Example Command

To run the application with a specific window resolution, detailed logging, and in camera emulation mode, you can use the following command:

```bash
python main.py --resolution 1280x720 --log-level DEBUG --emulate
```

This setup is ideal for development and testing on environments such as personal computers where real camera hardware is not available.

### Practical Usage

Using these command line options, you can tailor the application launch to fit various scenarios—from full deployment on a Raspberry Pi with actual camera hardware to a development setup on a PC. This flexibility facilitates easy testing and debugging, streamlining the development process for GeoPhoto.
