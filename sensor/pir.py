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
old_i = -1
try:
    while True:
        i = GPIO.input(8)
        if i != old_i:
            r = requests.get(ip+":5000/peopleCount")
            f = open('../raw/pir0','w')
            f.write(str(r.text))
            f.close()
            old_i = i
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()