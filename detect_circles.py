import cv2
import numpy as np

# import raspi
# image = raspi.picture()

image = cv2.imread('marbles2.png')

if image.shape != (256, 256):
    image = cv2.resize(image, (256, 256))

# make image grayscale
reduced = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# find edges
thres = 22
reduced = cv2.Canny(reduced, thres, thres * 3)

# detect circles in the image
sensitivity = 1.2
min_dist_between_circles = 20
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

    # save the output image
    cv2.imwrite("reduced.png", reduced)
    cv2.imwrite("output.png", image)
