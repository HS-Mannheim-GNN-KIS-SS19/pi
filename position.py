import numpy as np


class Position(np.ndarray):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        np.ndarray.__init__(self, [x, y])
