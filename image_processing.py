import subprocess
import cv2
import imutils
from imutils import contours
from constants import IMAGE_PROCESSING
from position import Position


def nothing(x):
    pass


# TODO implement me plzz
def _get_reference_point_positions(image):
    return []


# TODO implement me plzz
def _get_absolute_eezybot_position(image):
    return []


# TODO implement me plzz
def _get_stretch_factor(image):
    stretch = 1.0
    reference_points = _get_reference_point_positions(image)
    return []


# TODO implement me plzz
def _resolve_marble_pos_relative_to_eezybot(marble_pos_relative_to_field, eezybot_pos_relative_to_field):
    return []


# TODO implement me plzz
def _calculate_distance_to_arm(image) -> (float, float):
    import random as r
    horizontal, vertical = r.random() * 100, r.random() * 100
    return horizontal, vertical


def _find_marbles(image, color_lower, color_upper):
    print("lower " + str(color_lower))
    print("upper " + str(color_lower))
    if image.shape != (256, 256, 3):
        image = cv2.resize(image, (256, 256))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, color_lower, color_upper)
    res = cv2.bitwise_and(image, image, mask=mask)
    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

    conts = cv2.findContours(res, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts = imutils.grab_contours(conts)

    if len(conts) > 0:
        conts = contours.sort_contours(conts)[0]

    detected_marbles = []
    for cont in conts:
        ((x, y), radius) = cv2.minEnclosingCircle(cont)
        if radius < 7:
            continue
        x, y, radius = int(x), int(y), int(radius)
        cv2.circle(image, (x, y), 2, (0, 0, 255), -1)
        cv2.circle(image, (x, y), radius, (255, 0, 0), 2)
        detected_marbles.append((x, y, radius))

    return detected_marbles


def _detect_with_python2(color_lower, color_upper):
    python = 'python2'
    completed_process = subprocess.run(
        [python, 'image_processing.py', '"' + str(color_lower) + '"', '"' + str(color_upper) + '"'])
    # parse list string to list object
    print(completed_process.stdout)
    return eval(completed_process.stdout)


def _get_absolute_marble_positions(image):
    if IMAGE_PROCESSING.use_python_2:
        coords = _detect_with_python2()
    else:
        image = cv2.imread('../images/pitest.jpg')
        if image is None:
            image = cv2.imread("images/pitest.jpg")

    import numpy as np
    lower_blue = np.array([100, 0, 0])
    upper_blue = np.array([255, 255, 255])
    coords = _find_marbles(image, lower_blue, upper_blue)

    return coords


"""Program Interface"""


def get_marble_position_relative_to_eezybot(image):
    stretch = _get_stretch_factor(image)
    eezybot_pos_relative_to_field = list(
        map(lambda pos: [x * y for x, y in zip(pos, stretch)], _get_absolute_eezybot_position(image)))
    marble_pos_relative_to_field = list(
        map(lambda pos: [stretch * coord for coord in pos], _get_absolute_marble_positions(image)))
    return _resolve_marble_pos_relative_to_eezybot(eezybot_pos_relative_to_field, marble_pos_relative_to_field)


# TODO implement me plzz
def get_arm_position_relative_to_eezybot(image):
    return Position(0, 0)
