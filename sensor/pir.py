#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN)
old_i = -1
try:
    while True:
        i = GPIO.input(8)
        if i != old_i:
            f = open('../raw/pir0','w')
            f.write(str(i))
            f.close()
            old_i = i
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()