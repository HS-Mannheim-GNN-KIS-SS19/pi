from constants import AI
from image_processing import detect

env_properties = AI.properties.env


def get_state():
    map = detect(*env_properties.target_color_space)
    marbles = map["marbles"]

    if marbles is None or len(marbles) == 0:
        return tuple([0, 0, 0])

    biggest = marbles[0]
    for i in range(len(marbles)):
        if marbles[i][2] > biggest[2]:
            biggest = marbles[i]

    scale = 2.0 / map["shape"][0]
    return tuple(
        [env_properties.input_data_type(
            (round(x * env_properties.input_grid_radius * scale + 1.0))) for x in biggest])


if __name__ == '__main__':
    print(get_state())
