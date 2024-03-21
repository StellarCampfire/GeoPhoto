from picamera2 import Picamera2

picam2a = Picamera2(0)
picam2b = Picamera2(1)
picam2a.start()
picam2b.start()
picam2a.capture_file("cam0.jpg")
picam2b.capture_file("cam1.jpg")
picam2a.stop()
picam2b.stop()