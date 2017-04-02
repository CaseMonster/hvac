#===========================================================================================
#init

import RPi.GPIO as GPIO
import time
import datetime
import os
import serial
from twython import Twython

CONSUMER_KEY = 'CRTXD3XeoPoULULtyjc9Vt2Oy'
CONSUMER_SECRET = 'OTRUySjYqFjiEpcYb1yIDwk5EfylVjpuuNKJ9P0LqV7D9hIK0s'
ACCESS_KEY = '816423364487249920-3bCaGTZlbu8CJ4qcR75PusFNINpy8Ig'
ACCESS_SECRET = 'EehSQWPXwkT1aTfBheHSPXENlnq1Sl20rvuw6mpjmdskl'
TWEET = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET) 

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")
temp_sensor = "/sys/bus/w1/devices/28-0115722a0bff/w1_slave"

ser = serial.Serial(port='/dev/ttyAMA0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

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

#===========================================================================================
#definitions

STATUS_TEMP = "idle"
STATUS_HVAC = "idle"
STATUS_OLD = "idle"

HVAC_COOL = "on"
HVAC_HEAT = "on"

TEMP = 70
TEMP_SETTING_COOL = 74
TEMP_SETTING_HEAT = 69

COOLDOWN_TIMEOUT = 500
TIMER = 0
RUNTIME_MAX = 720
RUNTIME_MIN = 300

ERROR_TEMP_MAX = 85
ERROR_TEMP_MIN = 60
HEARTBEAT = True

#===========================================================================================
#functions

def CheckTemp():
	f = open(temp_sensor, 'r')
	lines = f.readlines()
	f.close()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = temp_raw()
	temp_output = lines[1].find('t=')
	if temp_output != -1:
		temp_string = lines[1].strip()[temp_output+2:]
		temp_c = float(temp_string) / 1000.0
		temp_f = temp_c * 9.0 / 5.0 + 32.0
		temp_f = temp_f + 1 #calibration
		return temp_f

def SetStatusTemp(): 
        if(TEMP > TEMP_SETTING + TEMP_THRESHOLD):
                return "cool"
        if(TEMP < TEMP_SETTING - TEMP_THRESHOLD):
                return "heat"
	return "idle"

def SetStatusHVAC():
        if((TEMP > ERROR_TEMP_MAX) or (TEMP < ERROR_TEMP_MIN)):
                return "error"
        if(STATUS_HVAC == "cool" and STATUS_TEMP == "heat"):
                return "error"
        if(STATUS_HVAC == "heat" and STATUS_TEMP == "cool"):
                return "error"
        if(STATUS_HVAC == "cooldown"):
                if(TIMER < COOLDOWN_TIMEOUT):
                        return "cooldown"
        if(STATUS_HVAC == "cool"):
                if(HVAC_COOL == "off"):
                        return "idle"
                if(TIMER < RUNTIME_MIN):
                        return "cool"
                if(TIMER > RUNTIME_MAX):
                        return "cooldown"
                if(TEMP > TEMP_SETTING_COOL):
                        return "cool"
                return "cooldown"
        if(STATUS_HVAC == "heat"):
                if(HVAC_HEAT == "off"):
                        return "idle"
                if(TIMER < RUNTIME_MIN):
                        return "heat"
                if(TIMER > RUNTIME_MAX):
                        return "cooldown"
                if(TEMP < TEMP_SETTING_HEAT):
                        return "heat"
                return "cooldown"
        if(STATUS_TEMP == "cool"):
                return "cool"
        if(STATUS_TEMP == "heat"):
                return "heat"                
        return "idle"

def TurnOnCool():
        GPIO.output(PIN_COOL, GPIO.HIGH)
        GPIO.output(PIN_COOL_LED, GPIO.HIGH)

def TurnOnHeat():
        GPIO.output(PIN_HEAT, GPIO.HIGH)
        GPIO.output(PIN_HEAT_LED, GPIO.HIGH)

def TurnOffEverything():
	GPIO.output(PIN_HEAT, GPIO.LOW)
	GPIO.output(PIN_COOL, GPIO.LOW)
	GPIO.output(PIN_HEAT_LED, GPIO.LOW)
	GPIO.output(PIN_COOL_LED, GPIO.LOW)

def CheckTimer():
        if(HVAC_STATUS == OLD_STATUS):
                return TIMER
        return 0

def Heartbeat():
        t = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        s = str(t + " \t " + "HVAC STAUS: " + str(HVAC_STATUS) + " \t " + "TEMP STATUS: " + str(TEMP_STATUS) + " \t " + "TEMP: " + str(TEMP) + " \t " + " TIMER: " + str(TIMER))
        print(s)
        if(TIMER % 100 == 0):
                try:
                        TWEET.update_status(status = s)
                except:
                        print(t + " ********** TWEET FAILED **********")
        temp = not HEARTBEAT
        GPIO.output(PIN_STATUS_LED, HEARTBEAT)
        return temp

def Hello():
        t = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        print(t + " ********** HVAC STARTED **********")
        try:
                TWEET.update_status(status = t + " ********** HVAC STARTED **********")
        except:
                print(t + " ********** TWEET FAILED **********")

def SerialReceive():
        return ser.readline()   

def SerialSend():
        #temp, temp heat, temp cold, heat on/off, cool on/off
        string = str(TEMP + " " + TEMP_SETTING_HEAT+ " " + TEMP_SETTING_COOL+ " " + HVAC_HEAT+ " " + HVAC_COOL)
        ser.write(string)

#===========================================================================================
#main

Hello()
TurnOffEverything()

while True:
        #pre
        HEARTBEAT = Heartbeat()
	TEMP = CheckTemp()

	#check temp/communicate to head unit
	SerialReceive()
	if(string == "TEMP_HEAT_UP"):
                TEMP_SETTING_UPPER = TEMP_SETTING_HEAT + 1
        if(string == "TEMP_HEAT_DN"):
                TEMP_SETTING_UPPER = TEMP_SETTING_HEAT - 1
        if(string == "TEMP_COOL_UP"):
                TEMP_SETTING_UPPER = TEMP_SETTING_COOL + 1
        if(string == "TEMP_COOL_DN"):
                TEMP_SETTING_UPPER = TEMP_SETTING_COOL - 1
        if(string == "TEMP_HEAT_ON"):
                HVAC_HEAT = "on"
        if(string == "TEMP_HEAT_OFF"):
                HVAC_HEAT = "off"
        if(string == "TEMP_COOL_ON"):
                HVAC_COOL = "on"
        if(string == "TEMP_COOL_OFF"):
                HVAC_COOL = "off"

	#check status/communicate to hvac
        STATUS_TEMP = SetStatusTemp()
        STATUS_HVAC = SetStatusHVAC()
        if(STATUS_HVAC == "cool"):
                TurnOnCool()
        if(STATUS_HVAC == "heat"):
                TurnOnHeat()
        if(STATUS_HVAC == "cooldown"):
                TurnOffEverything()
	if(STATUS_HVAC == "idle"):
                TurnOffEverything()
        if(STATUS_HVAC == "error"):
                TurnOffEverything()

        #post
        SerialSend()
	time.sleep(.3)
	TIMER = TIMER + 1
	TIMER = CheckTimer()
	STATUS_OLD = STATUS_HVAC
