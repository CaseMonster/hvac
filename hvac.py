#===========================================================================================
#init

import RPi.GPIO as GPIO
import time
import os

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")
temp_sensor = "/sys/bus/w1/devices/28-0115722a0bff/w1_slave"

#===========================================================================================
#pin setup

GPIO.setmode(GPIO.BOARD)
PIN_COOL = 38
PIN_HEAT = 36
PIN_STATUS = 40
GPIO.setup(PIN_STATUS, GPIO.OUT)
GPIO.setup(PIN_HEAT, GPIO.OUT)
GPIO.setup(PIN_COOL, GPIO.OUT)

GPIO.output(PIN_STATUS, GPIO.LOW)
GPIO.output(PIN_HEAT, GPIO.LOW)
GPIO.output(PIN_COOL, GPIO.LOW)

#===========================================================================================
#definitions

COOLDOWN_TIMEOUT = 360
TEMP_THRESHOLD = 3
TEMP_SETTING = 72
TEMP_STATUS = "idle"
HVAC_STATUS = "idle"

CURRENT_TEMP = 70
CURRENT_RUNTIME = 0
CURRENT_IDLE = 0
CURRENT_COOLDOWN = 0
RUNTIME_MAX = 720
RUNTIME_MIN = 300

ERROR_TEMP_MAX = 85
ERROR_TEMP_MIN = 60
ERROR = False
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
		return temp_f

def CheckForStrangeTemp():
	if((CURRENT_TEMP > ERROR_TEMP_MAX) or (CURRENT_TEMP < ERROR_TEMP_MIN)):
		return True
	return False

def SetStatusTemp(): 
        if(CURRENT_TEMP > TEMP_SETTING + TEMP_THRESHOLD):
                return "cool"
        if(CURRENT_TEMP < TEMP_SETTING - TEMP_THRESHOLD):
                return "heat"
	return "idle"

def SetStatusHVAC():
        if(HVAC_STATUS == "cool" and TEMP_STATUS == "heat"):
                return "error"
        if(HVAC_STATUS == "heat" and TEMP_STATUS == "cool"):
                return "error"
        if(HVAC_STATUS == "cool"):
                if(CURRENT_RUNTIME < RUNTIME_MIN):
                        return "cool"
        if(HVAC_STATUS == "heat"):
                if(CURRENT_RUNTIME < RUNTIME_MIN):
                        return "heat"
        if(TEMP_STATUS == "cool" or TEMP_STATUS == "heat" or HVAC_STATUS == "cooldown"):
                if(CURRENT_COOLDOWN > COOLDOWN_TIMEOUT):
                        return "cooldown"
                if(TEMP_STATUS == "cool"):
                        return "cool"
                if(TEMP_STATUS == "heat"): 
                        return "heat"
        return "idle"

def TurnOnCool():
	GPIO.output(PIN_COOL, GPIO.HIGH)

def TurnOnHeat():
	GPIO.output(PIN_HEAT, GPIO.HIGH)

def TurnOffEverything():
	GPIO.output(PIN_HEAT, GPIO.LOW)
	GPIO.output(PIN_COOL, GPIO.LOW)

def Heartbeat(HEARTBEAT):
        temp = not HEARTBEAT
        GPIO.output(PIN_STATUS, HEARTBEAT)
        return temp

#===========================================================================================
#main

print("start")
while True:
        
	CURRENT_TEMP = CheckTemp()
	print("temp - " + str(CURRENT_TEMP))

	#getSetting()

        TEMP_STATUS = SetStatusTemp()
        print("temp status - " + TEMP_STATUS)

        HVAC_STATUS = SetStatusHVAC()
        print("hvac status - " + HVAC_STATUS)

        if(HVAC_STATUS == "cool"):
                print("cooling")
                TurnOnCool()

        if(HVAC_STATUS == "heat"):
                print("heating")
                TurnOnHeat()

        if(HVAC_STATUS == "cool" or HVAC_STATUS == "heat"):
                CURRENT_IDLE = 0
                CURRENT_COOLDOWN = 0
                CURRENT_RUNTIME = CURRENT_RUNTIME + 1

        if(HVAC_STATUS == "cooldown"):
                TurnOffEverything()
                CURRENT_RUNTIME = 0
                CURRENT_COOLDOWN = CURRENT_COOLDOWN + 1
                
	if(HVAC_STATUS == "idle"):
                TurnOffEverything()
                CURRENT_COOLDOWN = 0
                CURRENT_RUNTIME = 0
		CURRENT_IDLE = CURRENT_IDLE + 1

        ERROR = CheckForStrangeTemp()
        if(ERROR or HVAC_STATUS == "error"):
                print("error")
                print("turning off hvac")
                TurnOffEverything()
                raw_input("pausing on error")

	print("runtime " + str(CURRENT_RUNTIME) + " \ cooldown " + str(CURRENT_COOLDOWN) + " \ idle " + str(CURRENT_IDLE))
	time.sleep(.1)
	HEARTBEAT = Heartbeat(HEARTBEAT)

print("end")
