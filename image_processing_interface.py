from image_processing import detect


# returns Position of the marble as Position Object
def get_state():
    map = detect((100, 0, 0), (255, 255, 255))
    marbles = map["marbles"]

    biggest = marbles[0]
    for i in range(len(marbles)):
        if marbles[i][2] > biggest[2]:
            biggest = marbles[i]

    scale = 2.0 / map["shape"][0]
    return tuple([x * scale + 1.0 for x in biggest])


if __name__ == '__main__':
    print(get_state())
