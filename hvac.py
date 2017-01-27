#===========================================================================================
#init

import RPi.GPIO as GPIO
import time
import datetime
import os
from twython import Twython

CONSUMER_KEY = 'CRTXD3XeoPoULULtyjc9Vt2Oy'
CONSUMER_SECRET = 'OTRUySjYqFjiEpcYb1yIDwk5EfylVjpuuNKJ9P0LqV7D9hIK0s'
ACCESS_KEY = '816423364487249920-3bCaGTZlbu8CJ4qcR75PusFNINpy8Ig'
ACCESS_SECRET = 'EehSQWPXwkT1aTfBheHSPXENlnq1Sl20rvuw6mpjmdskl'
TWEET = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET) 

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")
temp_sensor = "/sys/bus/w1/devices/28-0115722a0bff/w1_slave"

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

COOLDOWN_TIMEOUT = 500
TEMP_THRESHOLD = 2.5
TEMP_SETTING = 72
TEMP_STATUS = "idle"
HVAC_STATUS = "idle"
OLD_STATUS = "idle"

TEMP = 70
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
		temp_f = temp_f + 2 #calibration
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
        if(HVAC_STATUS == "cool" and TEMP_STATUS == "heat"):
                return "error"
        if(HVAC_STATUS == "heat" and TEMP_STATUS == "cool"):
                return "error"
        if(HVAC_STATUS == "cooldown"):
                if(TIMER < COOLDOWN_TIMEOUT):
                        return "cooldown"
        if(HVAC_STATUS == "cool"):
                if(TIMER < RUNTIME_MIN):
                        return "cool"
                if(TIMER > RUNTIME_MAX):
                        return "cooldown"
                if(TEMP > (TEMP_SETTING + TEMP_THRESHOLD / 2)):
                        return "cool"
                return "cooldown"
        if(HVAC_STATUS == "heat"):
                if(TIMER < RUNTIME_MIN):
                        return "heat"
                if(TIMER > RUNTIME_MAX):
                        return "cooldown"
                if(TEMP < (TEMP_SETTING - TEMP_THRESHOLD / 2)):
                        return "heat"
                return "cooldown"
        if(TEMP_STATUS == "cool"):
                return "cool"
        if(TEMP_STATUS == "heat"):
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
        s = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " \t " + "HVAC STAUS: " + str(HVAC_STATUS) + " \t " + "TEMP STATUS: " + str(TEMP_STATUS) + " \t " + "TEMP: " + str(TEMP) + " \t " + " TIMER: " + str(TIMER))
        print(s)
        if(TIMER % 100 == 0):
                try:
                        TWEET.update_status(status = s)
                except:
                        print("********** TWEET FAILED **********")
        temp = not HEARTBEAT
        GPIO.output(PIN_STATUS_LED, HEARTBEAT)
        return temp

def Hello():
        print("********** HVAC STARTED **********")
        TWEET.update_status(status = "********** HVAC STARTED **********")

#===========================================================================================
#main

Hello()
TurnOffEverything()

while True:
        HEARTBEAT = Heartbeat()
        
	TEMP = CheckTemp()
	#getSetting()
	
        TEMP_STATUS = SetStatusTemp()
        HVAC_STATUS = SetStatusHVAC()
        
        if(HVAC_STATUS == "cool"):
                TurnOnCool()
        if(HVAC_STATUS == "heat"):
                TurnOnHeat()
        if(HVAC_STATUS == "cooldown"):
                TurnOffEverything()
	if(HVAC_STATUS == "idle"):
                TurnOffEverything()
        if(HVAC_STATUS == "error"):
                TurnOffEverything()
                
	time.sleep(.3)
	
	TIMER = TIMER + 1
	TIMER = CheckTimer()
	OLD_STATUS = HVAC_STATUS
