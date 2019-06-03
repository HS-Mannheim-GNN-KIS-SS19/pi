from constants import _I_ENV_PROPERTIES
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
    return tuple(
        [_I_ENV_PROPERTIES.INPUT_DATA_TYPE((round(x * _I_ENV_PROPERTIES.INPUT_GRID_RADIUS * scale + 1.0))) for x in
         biggest])


if __name__ == '__main__':
    print(get_state())
