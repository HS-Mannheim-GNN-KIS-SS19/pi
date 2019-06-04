import time

from picamera import PiCamera
from picamera.array import PiRGBArray

camera = None


def take_picture():
    global camera

    if camera is None:
        camera = PiCamera()
        camera.resolution = (1024, 1024)
        # allow the camera to warmup
        time.sleep(1)

    raw_capture = PiRGBArray(camera)

    # grab an image from the camera
    camera.capture(raw_capture, format="bgr")
    image = raw_capture.array

    if image is None:
        raise AssertionError("no image")
    return image
