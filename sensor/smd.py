#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import sys
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

off = 0x000000

pinsLed = {'R':11,'G':12,'B':13}
for i in pinsLed:
    GPIO.setup(pinsLed[i],GPIO.OUT)
p_R = GPIO.PWM(pinsLed['R'],2000)
p_G = GPIO.PWM(pinsLed['G'],2000)
p_B = GPIO.PWM(pinsLed['B'],5000)

p_R.start(0)
p_G.start(0)
p_B.start(0)

def map(x,in_min,in_max,out_min,out_max):
    return(x-in_min)*(out_max-out_min)/(in_max-in_min)+(out_min)

def setColor(col):
    p_R.ChangeDutyCycle(map(((col&0x110000)>>16),0,255,0,100))
    p_G.ChangeDutyCycle(map(((col&0x001100)>>8),0,255,0,100))
    p_B.ChangeDutyCycle(map(((col&0x000011)>>0),0,255,0,100))
    return

try:
    while True:
        setColor(off)
        f = open('../raw/ldr0','r')
        ldr = float(f.read())
        f.close()
        f = open('../raw/pir0','r')
        pir = int(f.read())
        f.close()
        f = open('../raw/smd0','r')
        on = int(f.read(),16)
        f.close()
        if pir > 0:
            if ldr >= 0.6:
                setColor(on)
            else:
                setColor(off)
        else:
            setColor(off)
        time.sleep(1)
except KeyboardInterrupt:
    p_R.stop()
    p_G.stop()
    p_B.stop()
    for i in pinsLed:
        GPIO.output(pinsLed[i],GPIO.LOW)
    GPIO.cleanup()
