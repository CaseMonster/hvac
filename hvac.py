#!/usr/bin/env python
#===========================================================================================
#init

import RPi.GPIO as GPIO
import time
import os

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")
temp_sensor = "/sys/bus/w1/devices/28-0416239f59ff/w1_slave"

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
#vars

STATUS_TEMP = "idle"
STATUS_HVAC = "idle"
STATUS_OLD = "idle"

HVAC_COOL = "off"
HVAC_HEAT = "off"

TEMP = 70
TEMP_SETTING_COOL = 75
TEMP_SETTING_HEAT = 68

COOLDOWN_TIMEOUT = 8
TIMER = 0
RUNTIME_MAX = 12
RUNTIME_MIN = 4

ERROR_TEMP_MAX = 85
ERROR_TEMP_MIN = 45
HEARTBEAT = True

#===========================================================================================
#functions

def CheckTemp():
        try:
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
                        temp_f = temp_f #calibration
                        return temp_f
        except:
                print(" ********** SENSOR FAILED **********")
                return 999

def SetStatusTemp(): 
        if(TEMP > TEMP_SETTING_COOL):
                return "cool"
        if(TEMP < TEMP_SETTING_HEAT):
                return "heat"
	return "idle"

def SetStatusHVAC():
        if(STATUS_HVAC == "error"):
                return "error"
        if((TEMP > ERROR_TEMP_MAX) or (TEMP < ERROR_TEMP_MIN)):
                return "error"
        if(STATUS_HVAC == "cool" and STATUS_TEMP == "heat"):
                return "error"
        if(STATUS_HVAC == "heat" and STATUS_TEMP == "cool"):
                return "error"
        if(STATUS_HVAC == "cooldown"):
                if(TIMER < COOLDOWN_TIMEOUT * 60):
                        return "cooldown"
        if(STATUS_HVAC == "cool"):
                if(TIMER < RUNTIME_MIN * 60):
                        return "cool"
                if(TIMER > RUNTIME_MAX * 60):
                        return "cooldown"
                if(TEMP > TEMP_SETTING_COOL):
                        return "cool"
                return "cooldown"
        if(STATUS_HVAC == "heat"):
                if(TIMER < RUNTIME_MIN * 60):
                        return "heat"
                if(TIMER > RUNTIME_MAX * 60):
                        return "cooldown"
                if(TEMP < TEMP_SETTING_HEAT):
                        return "heat"
                return "cooldown"
        if((STATUS_TEMP == "cool") and (HVAC_COOL == "on")):
                return "cool"
        if((STATUS_TEMP == "heat") and (HVAC_HEAT == "on")):
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
        if(STATUS_HVAC == STATUS_OLD):
                return TIMER
        return 0

def SetOutput():
        try:
                log = open("/ramtmp/hvac.output","w")
                log.write(str(TEMP) + "\n")
                log.write(str(STATUS_HVAC) + "\n")
                log.close()
        except:
                print(" ********** WRITE CONFIG FAILED **********")

def GetConfig():
        global HVAC_COOL
        global HVAC_HEAT
        global TEMP_SETTING_COOL
        global TEMP_SETTING_HEAT
        global COOLDOWN_TIMEOUT
        global RUNTIME_MAX
        global RUNTIME_MIN

        try:
                log = open("/ramtmp/hvac.config","r")
                HVAC_COOL = log.readline().rstrip('\r\n')
                HVAC_HEAT = log.readline().rstrip('\r\n')
                TEMP_SETTING_COOL = int(log.readline().rstrip('\r\n'))
                TEMP_SETTING_HEAT = int(log.readline().rstrip('\r\n'))
                COOLDOWN_TIMEOUT = int(log.readline().rstrip('\r\n'))
                RUNTIME_MAX = int(log.readline().rstrip('\r\n'))
                RUNTIME_MIN = int(log.readline().rstrip('\r\n'))
                log.close()
        except:
                print(" ********** READ CONFIG FAILED **********")

def Heartbeat():
        s = str("CFG: " + str(HVAC_COOL) + " " + str(HVAC_HEAT) + "\t HVAC: " + str(STATUS_HVAC) + "\t THRM: " + str(STATUS_TEMP) + "\t f: " + str(TEMP) + "\t TICK: " + str(TIMER))
        print(s)
        temp = not HEARTBEAT
        GPIO.output(PIN_STATUS_LED, HEARTBEAT)
        return temp

#===========================================================================================
#main

TurnOffEverything()

while True:
        #pre
        HEARTBEAT = Heartbeat()
	TEMP = CheckTemp()

	#check temp/communicate to head unit
        GetConfig()

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
	time.sleep(.2)
	SetOutput()
	TIMER = TIMER + 1
	TIMER = CheckTimer()
	STATUS_OLD = STATUS_HVAC
