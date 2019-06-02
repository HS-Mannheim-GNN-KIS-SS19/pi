from constants import ENV
from image_processing import detect


def get_state():
    map = detect((100, 0, 0), (255, 255, 255))
    marbles = map["marbles"]

    if marbles is None or len(marbles) == 0:
        return tuple([0, 0, 0])

    biggest = marbles[0]
    for i in range(len(marbles)):
        if marbles[i][2] > biggest[2]:
            biggest = marbles[i]

    scale = 2.0 / map["shape"][0]
    return tuple([int(round(x * ENV.INPUT_RANGE * scale + 1.0)) for x in biggest])


if __name__ == '__main__':
    print(get_state())
