import cv2
import numpy as np
import time
from detect_shapes import find_marbles
import raspi_camera

while True:
    start_time = time.time()

    image = raspi_camera.picture()
    #image = cv2.imread('pitest.jpg')
    coords = find_marbles(image)

    print('found {} marbles at {}'.format(len(coords), coords))

    print("took {:1.0f} ms for calculations".format((time.time() - start_time) * 1000))
    print('----------------')

    cv2.imshow('live view', image)
    cv2.waitKey(1)

# cv2.imshow('image', image)
# k = cv2.waitKey(0) & 0xFF
# # esc pressed
# if k == 27:
#     exit()
