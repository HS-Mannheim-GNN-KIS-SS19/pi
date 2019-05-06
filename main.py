import cv2
import numpy as np
import time
from detect_shapes import *

DEBUG = True


def main():
    while True:
        start_time = time.time()

        image = None
        coords = detect_with_python2()

        # image = cv2.imread('pitest.jpg')
        # coords = find_marbles(image)

        print('found {} marbles at {}'.format(len(coords), coords))

        print("took {:1.0f} ms for calculations".format((time.time() - start_time) * 1000))
        print('----------------')

        if image is not None:
            cv2.imshow('live view', image)
            cv2.waitKey(1)


if __name__ == '__main__':
    main()
