import image_processing
import move_to

from eezybotServoController import eezybot

while True:
    x, y = image_processing.find_marbles()[0]
    move_to.move_to(x, y)
    eezybot.clutch.grab()
    x, y = image_processing.find_destination()
    move_to.move_to(x, y)
    eezybot.clutch.release()
