from __future__ import division
import math
import time
import Adafruit_PCA9685

#for handeling ctrl+C
import signal
import sys

pwm = Adafruit_PCA9685.PCA9685()

servo_min = 150
servo_max = 600
servo_mid = (int)((servo_min + servo_max)/2)
servo_range = servo_max - servo_min

#change accordingly
front_left  = 1
front_right = 2
back_left   = 3
back_right  = 4
head        = 0

def reset():
    pwm.set_pwm(head, 0, servo_mid)
    pwm.set_pwm(front_left, 0, servo_mid)
    pwm.set_pwm(front_right, 0, servo_mid)
    pwm.set_pwm(back_left, 0, servo_mid)
    pwm.set_pwm(back_right, 0, servo_mid)

#for handeling ctrl+C
def signal_handler(sig, frame):
        reset()
        sys.exit(0)

pwm.set_pwm_freq(60)


x = 0
print("Please set the speed (0.01 is slow, 0.3 is fast)")
speed = input()
reset()
time.sleep(2)
print('Walking starting, press Ctrl-C to quit')

#for handeling ctrl+C
signal.signal(signal.SIGINT, signal_handler)

#for i in range (0,200):
while True:
    #print ("sin(",x,") : ", (int)((math.sin(x)*0.4+0.5)*servo_range+servo_min))
    #print ("cos(",x,") : ", (int)((math.cos(x)*0.4+0.5)*servo_range+servo_min))
    front_right_value = (int)(((math.sin(x)*0.1+0.5)*servo_range)+servo_min)
    front_left_value = (int)(((math.sin(x)*0.1+0.5)*servo_range)+servo_min)
    back_right_value  = (int)(((math.cos(x)*0.1+0.5)*servo_range)+servo_min)
    back_left_value  = (int)(((math.cos(x)*0.1+0.5)*servo_range)+servo_min)
    pwm.set_pwm(front_right, 0, front_right_value)
    pwm.set_pwm(front_left, 0, front_left_value)
    pwm.set_pwm(back_right, 0, back_right_value)
    pwm.set_pwm(back_left, 0, back_left_value)
    #print(x)
    
    #larger addition = more speed!
    x += speed
    
    if(x > math.pi*2):
      x -= math.pi*2

#for handeling ctrl+C
signal.pause()
