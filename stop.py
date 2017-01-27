#===========================================================================================
#init

import RPi.GPIO as GPIO
import os

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")

#===========================================================================================
#pin setup

GPIO.setmode(GPIO.BOARD)
PIN_STATUS_LED = 40
PIN_COOL_LED = 38
PIN_COOL = 37
PIN_HEAT_LED = 36
PIN_HEAT = 35
GPIO.setup(PIN_STATUS_LED, GPIO.OUT)
GPIO.setup(PIN_COOL_LED, GPIO.OUT)
GPIO.setup(PIN_COOL, GPIO.OUT)
GPIO.setup(PIN_HEAT_LED, GPIO.OUT)
GPIO.setup(PIN_HEAT, GPIO.OUT)

GPIO.output(PIN_HEAT, GPIO.LOW)
GPIO.output(PIN_COOL, GPIO.LOW)
GPIO.output(PIN_HEAT_LED, GPIO.LOW)
GPIO.output(PIN_COOL_LED, GPIO.LOW)
