import subprocess
import sys

camera_num = sys.argv[1] if len(sys.argv) > 1 else 0

command = f'libcamera-still --camera {camera_num} --nopreview -o test.jpg'

process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

stdout, stderr = process.communicate()

print("stdout:", stdout)
print("stderr:", stderr)
