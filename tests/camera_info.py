from picamera2 import Picamera2

print("_______________________________________________")
camera_info = Picamera2.global_camera_info()
for camera in camera_info:
    print(camera)
print("_______________________________________________")