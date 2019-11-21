#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import adc0832
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
adc0832.setup()

def remap(x,in_min,in_max,out_min,out_max):
    return round((((x-in_min)*(out_max-out_min))/(in_max-in_min)+out_min),2)

try:
    while True:
        fin = open('../raw/ldr0','w')
        fin.write(str(remap(adc0832.getResult(),0,255,0,1)))
        fin.close()
        time.sleep(5)
except KeyboardInterrupt:
    adc0832.destroy()
    GPIO.cleanup()