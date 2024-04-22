import os
import subprocess


def build_ui_files(ui_path=os.path.join('.', 'resources', 'ui'), py_path=os.path.join('.', 'resources', 'py')):
    os.makedirs(py_path, exist_ok=True)

    for ui_file in os.listdir(ui_path):
        if ui_file.endswith('.ui'):
            ui_file_path = os.path.join(ui_path, ui_file)
            py_file_path = os.path.join(py_path, f"{os.path.splitext(ui_file)[0]}.py")
            print(f"Building {ui_file}...")

            subprocess.run(['pyuic5', '-x', ui_file_path, '-o', py_file_path], check=True)

    print("UI build process completed!")


if __name__ == "__main__":
    build_ui_files()
