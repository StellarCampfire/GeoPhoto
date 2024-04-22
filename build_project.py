import os
import subprocess
import argparse
from build_ui import build_ui_files


def build_project(target_os):
    base_path = os.path.dirname(__file__)
    resources_path = os.path.join(base_path, "resources")

    styles_path = os.path.join(resources_path, "styles")
    animations_path = os.path.join(resources_path, "animations")
    icon_path = os.path.join(resources_path, "icons", "geological.png")

    os_pathsep = ';' if target_os == 'windows' else ':'

    command = [
        'pyinstaller',
        '--add-data', f"{styles_path}{os_pathsep}resources/styles",
        '--add-data', f"{animations_path}{os_pathsep}resources/animations",
        '--onefile',
        '--windowed',
        '-n', 'GeoPhoto',
        '-i', icon_path,
        'main.py'
    ]

    print("Running command:", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the PyQt5 application.")
    parser.add_argument('--os', type=str, default='windows', choices=['windows', 'linux'],
                        help='Target operating system for the build: windows or linux')
    parser.add_argument('--ui', action='store_true', help='Build UI files if set')
    args = parser.parse_args()

    if args.ui:
        build_ui_files()
    build_project(args.os)
