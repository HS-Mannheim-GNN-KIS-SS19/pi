import cv2
import numpy as np
import imutils
from imutils import contours
import time

# import raspi
# image = raspi.picture()

def nothing(x):
    pass


def transform(image, sensitivity, min_dist_between_circles, thres, ratio):
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


def main():
    start_time = time.time()
    image = cv2.imread('pitest2.jpg')

    if image.shape != (256, 256, 3):
        image = cv2.resize(image, (256, 256))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([80, 60, 0])
    upper_yellow = np.array([255, 255, 220])

    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    res = cv2.bitwise_and(image, image, mask=mask)

    res2 = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY);
    cnts = cv2.findContours(res2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = contours.sort_contours(cnts)[0]
    print("--- %s seconds ---" % (time.time() - start_time))
    # loop over the contours
    for (i, c) in enumerate(cnts):
        # draw the bright spot on the image
        (x, y, w, h) = cv2.boundingRect(c)
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        cv2.circle(image, (int(cX), int(cY)), int(radius),
                   (0, 0, 255), 2)
        print(str(int(cX)) + "   " + str(int(cY)))

    cv2.imshow('image <-> res', np.hstack([image, res]))
    cv2.imshow('mask', mask)
    k = cv2.waitKey(25000) & 0xFF


def main2():
    image = cv2.imread('handytest.jpg')
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

        image, reduced = transform(image_copy, sensitivity / 10, min_dist, thres, ratio)
        # orig_image, image = transform(image, 0.5, 1, 34, 4)
        cv2.imshow('image', np.hstack([reduced, image]))

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()
    # cv2.imwrite("reduced.png", reduced)
    # cv2.imwrite("output.png", image)


main()
