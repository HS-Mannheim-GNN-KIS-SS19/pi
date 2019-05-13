import time
import cv2

from image_processing_interface import *

IMAGE = None  # cv2.imread('pitest.jpg')


def findMarbles():
    start_time = time.time()
    coords = get_marbles(IMAGE)
    print('found {} marbles at {}'.format(len(coords), coords))
    print("took {:1.0f} ms for calculations".format((time.time() - start_time) * 1000))
    print('----------------')


def findArm():
    start_time = time.time()
    coords = get_arm(IMAGE)
    print('found Arm at {}'.format(coords))
    print("took {:1.0f} ms for calculations".format((time.time() - start_time) * 1000))
    print('----------------')


def findDestination():
    start_time = time.time()
    coords = get_destination(IMAGE)
    print('found Destination at {}'.format(coords))
    print("took {:1.0f} ms for calculations".format((time.time() - start_time) * 1000))
    print('----------------')


def main():
    start_time = time.time()
    findMarbles()
    findArm()
    findDestination()
    print("All done")
    print("took {:1.0f} ms for calculations".format((time.time() - start_time) * 1000))
    print('----------------')
    if IMAGE is not None:
        cv2.imshow('live view', IMAGE)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
