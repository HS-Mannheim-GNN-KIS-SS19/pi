class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __format__(self, format):
        return "x:{}, y:{}".format(self.x, self.y)
