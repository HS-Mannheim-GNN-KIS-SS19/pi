#import wiringpi as wp
#from picamera import PiCamera
from io import BytesIO
import PIL as pil
import sys
from tkinter import *

def camera():
    camera = PiCamera()
    camera.resolution = (256, 256)
    camera.capture('img.png')
    """
    stream = BytesIO()
    camera.capture(stream, format='png')
    stream.seek(0)

    image = pil.Image.open(stream)
    """
    

def robot():
    # sequential pin numbering
    wp.wiringPiSetup()

if len(sys.argv) > 1:
    if sys.argv[1] == '-c':
        camera()
    elif sys.argv[1] == '-r':
        robot()

else:
    main = Tk()

    frame = Frame(main, width=100, height=100)
    main.bind('<Left>', lambda x: print(x))
    main.bind('<Right>', lambda x: print(x))
    main.bind('<Up>', lambda x: print(x))
    main.bind('<Down>', lambda x: print(x))

    frame.pack()
    main.mainloop()