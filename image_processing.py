import subprocess
import sys

import cv2
import imutils
import numpy as np
from imutils import contours

from constants import IMAGE_PROCESSING


def _find_marbles(image, color_lower, color_upper):
    if image.shape != (256, 256, 3):
        image = cv2.resize(image, (256, 256))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, color_lower, color_upper)
    res = cv2.bitwise_and(image, image, mask=mask)
    # cv2.imshow('image <-> res', np.hstack([image, res]))
    # cv2.imshow('mask', mask)
    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

    conts = cv2.findContours(res, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts = imutils.grab_contours(conts)

    if len(conts) > 0:
        conts = contours.sort_contours(conts)[0]

    detected_marbles = []
    for cont in conts:
        ((x, y), radius) = cv2.minEnclosingCircle(cont)
        if radius < IMAGE_PROCESSING.MIN_RADIUS:
            continue
        x, y, radius = int(x - 110), int(y), int(radius)
        cv2.circle(image, (x, y), 2, (0, 0, 255), -1)
        cv2.circle(image, (x, y), radius, (255, 0, 0), 2)
        detected_marbles.append((x, y, radius))

    return detected_marbles


def _main(color_lower, color_upper):
    if IMAGE_PROCESSING.USE_IMAGE_NOT_CAMERA:
        image = cv2.imread('images/pitest.jpg')
    else:
        import raspi_camera

        image = raspi_camera.take_picture()

    return {
        "shape": image.shape,
        "marbles": _find_marbles(image, np.array(color_lower), np.array(color_upper))
    }


def detect(color_lower, color_upper):
    if IMAGE_PROCESSING.EXECUTE_IN_PYTHON2:
        python = 'python2'
        cmdLine = [python, 'image_processing.py', '"' + str(color_lower) + '"', '"' + str(color_upper) + '"']
        completed_process = subprocess.run(cmdLine)
        # parse list string to list object
        print(completed_process.stdout)
        return eval(completed_process.stdout)
    return _main(color_lower, color_upper)


# called when executed directly
if __name__ == '__main__':
    print(_main(eval(sys.argv[1]), eval(sys.argv[2])))
