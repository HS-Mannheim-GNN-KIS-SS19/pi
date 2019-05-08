import subprocess
import sys

import cv2
import imutils
import numpy as np
from imutils import contours

DEBUG = True


def nothing(x):
    pass


def _old_transform(image, sensitivity, min_dist_between_circles, thres, ratio):
    if image.shape != (256, 256):
        image = cv2.resize(image, (256, 256))

    # make image grayscale
    reduced = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # find edges
    reduced = cv2.Canny(reduced, thres, thres * ratio)

    # detect circles in the image
    circles = cv2.HoughCircles(reduced, cv2.HOUGH_GRADIENT, sensitivity, min_dist_between_circles)
    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(image, (x, y), r, (0, 255, 0), 1)
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

    reduced = cv2.cvtColor(reduced, cv2.COLOR_GRAY2BGR)

    return image, reduced


# TODO implement me plzz
def calculate_distance_to_arm(image):
    x, y = 0, 0
    return x, y


def find_marbles(image, color_lower, color_upper):
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


def _old_main():
    image = cv2.imread('images/handytest.jpg')
    image_copy = image.copy()
    cv2.namedWindow('image')

    cv2.createTrackbar('sensitivity', 'image', 5, 100, nothing)
    cv2.createTrackbar('min_dist', 'image', 1, 200, nothing)
    cv2.createTrackbar('edges_threshold', 'image', 10, 100, nothing)
    cv2.createTrackbar('edges_threshold_ratio', 'image', 1, 10, nothing)

    while True:
        # get current positions of four trackbars
        sensitivity = cv2.getTrackbarPos('sensitivity', 'image')
        min_dist = cv2.getTrackbarPos('min_dist', 'image')
        thres = cv2.getTrackbarPos('edges_threshold', 'image')
        ratio = cv2.getTrackbarPos('edges_threshold_ratio', 'image')

        image, reduced = _old_transform(image_copy, sensitivity / 10, min_dist, thres, ratio)
        # orig_image, image = transform(image, 0.5, 1, 34, 4)
        cv2.imshow('image', np.hstack([reduced, image]))

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()
    # cv2.imwrite("reduced.png", reduced)
    # cv2.imwrite("output.png", image)


def detect_with_python2(color_lower, color_upper):
    python = 'python2'
    completed_process = subprocess.run(
        [python, 'detect_shapes.py', '"' + str(color_lower) + '"', '"' + str(color_upper) + '"'])
    # parse list string to list object
    print(completed_process.stdout)
    return eval(completed_process.stdout)


# called when executed directly
if __name__ == '__main__':
    if DEBUG:
        image = cv2.imread('images/pitest.jpg')
    else:
        import raspi_camera

        image = raspi_camera.picture()

    print(find_marbles(image, eval(sys.argv[1]), eval(sys.argv[2])))
