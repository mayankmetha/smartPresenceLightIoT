#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import requests
import sys
if len(sys.argv) != 2:
    print("Error: python3 <script> <ip address>")
    exit(0)
ip = sys.argv[1]
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN)
try:
    while True:
        i = GPIO.input(8)
        if i == 1:
            f = open('../raw/pir0','w')
            f.write(str(1))
            f.close()
        else:
            r = requests.get(ip+":5000/peopleCount")
            f = open('../raw/pir0','w')
            f.write(str(r.text))
            f.close()
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()