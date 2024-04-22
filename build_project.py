import sys
import os
import subprocess
import argparse


def build_project(target_os):
    base_path = os.path.dirname(__file__)
    resources_path = os.path.join(base_path, "resources")

    styles_path = os.path.join(resources_path, "styles")
    animations_path = os.path.join(resources_path, "animations")

    os_pathsep = ';' if target_os == 'windows' else ':'

    command = " ".join([
        'pyinstaller',
        '--add-data',
        f"resources\\styles{os_pathsep}resources\\styles",
        '--add-data',
        f"resources\\animations{os_pathsep}resources\\animations",
        '--onefile',
        '--windowed',
        'main.py'
    ])

    print(command)

    subprocess.run(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the PyQt5 application.")
    parser.add_argument('--os', type=str, default='windows', choices=['windows', 'linux'],
                        help='Target operating system for the build: windows or linux')
    args = parser.parse_args()

    build_project(args.os)
