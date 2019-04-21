from picamera.array import PiRGBArray
from picamera import PiCamera
import time

camera = None


def picture():
    global camera

    if camera is None:
        camera = PiCamera()
        camera.resolution = (256, 256)
        # allow the camera to warmup
        time.sleep(0.1)

    raw_capture = PiRGBArray(camera)

    # grab an image from the camera
    camera.capture(raw_capture, format="bgr")
    image = raw_capture.array

    return image
