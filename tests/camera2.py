from picamera2 import Picamera2, Preview
import time
picam2_0 = Picamera2(0)
picam2_1 = Picamera2(1)

camera_config = picam2_0.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")

picam2_0.configure(camera_config)
picam2_1.configure(camera_config)

picam2_0.start_preview(Preview.QTGL)
picam2_0.start()

time.sleep(2)

picam2_0.capture_file("test_camera_0.jpg")
picam2_1.capture_file("test_camera_1.jpg")