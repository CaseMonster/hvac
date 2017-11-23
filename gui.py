#!/usr/bin/env python
#===========================================================================================
#init

import datetime
import time
import sys
import yweather
import vlc
from PyQt4 import QtGui, QtCore
from twython import Twython
from weather import Weather

CONSUMER_KEY = 'vODk25RpPIMGkdwNG5aDTSHf7'
CONSUMER_SECRET = 'DDpHqywyPvEkUflnIaxyRCkQIW5GQodVUtZemaDwLUE1SY7mF3'
ACCESS_KEY = '929544340061478912-wQby3MaYsrokOv4Hw9cz5zqDbxcsNr0'
ACCESS_SECRET = 'B3CJVhYhp8lZGX6U0cKxvQHGAvoIwYn13KmpLU6chjy0C'
TWEET = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET) 

#===========================================================================================
#vars

HVAC_TEMP = 99
HVAC_TEMP_CAL = 0
HVAC_STATUS = "initializing"

HVAC_COOL = "off"
HVAC_HEAT = "on"
HVAC_AUTO = "off"

TEMP_SETTING_COOL = 75
TEMP_SETTING_HEAT = 68

SECURITY_IPC = "blank"
        
#===========================================================================================
#gui

class GUI(QtGui.QWidget):
    
    def __init__(self):
        super(GUI, self).__init__()
        
        self.showFullScreen()
        self.setWindowTitle('hvac')

        self.timer_update = QtCore.QTimer()
        self.timer_update.timeout.connect(lambda:self.Update())
        self.timer_update.start(1000) #1s

        self.timer_log = QtCore.QTimer()
        self.timer_log.timeout.connect(lambda:self.Log())
        self.timer_log.start(60000) #60s

        self.timer_tweet = QtCore.QTimer()
        self.timer_tweet.timeout.connect(lambda:self.Tweet())
        self.timer_tweet.start(300000) #5m

        self.timer_weather = QtCore.QTimer()
        self.timer_weather.timeout.connect(lambda:self.UpdateWeather())
        self.timer_weather.start(1800000) #30m

        #font setup
        font_main = QtGui.QFont("Segoe UI", 14)
        font_med = QtGui.QFont("Segoe UI", 36, QtGui.QFont.Bold)
        font_large = QtGui.QFont("Segoe UI", 72, QtGui.QFont.Bold)
        font_xlarge = QtGui.QFont("Segoe UI", 200, QtGui.QFont.Bold) 

        #menu

        self.menu_main = QtGui.QPushButton('Main', self)
        self.menu_main.clicked.connect(lambda:self.ShowMain())
        self.menu_main.move(0, 380)
        self.menu_main.setFixedSize(100, 100)
        self.menu_main.setFont(font_main)
        self.menu_main.show()
        
        self.menu_weather = QtGui.QPushButton('Weather', self)
        self.menu_weather.clicked.connect(lambda:self.ShowWeather())
        self.menu_weather.move(100, 380)
        self.menu_weather.setFixedSize(100, 100)
        self.menu_weather.setFont(font_main)
        self.menu_weather.show()

        self.menu_settings = QtGui.QPushButton('Settings', self)
        self.menu_settings.clicked.connect(lambda:self.ShowSettings())
        self.menu_settings.move(200, 380)
        self.menu_settings.setFixedSize(100, 100)
        self.menu_settings.setFont(font_main)
        self.menu_settings.show()

        self.menu_Security = QtGui.QPushButton('Security', self)
        self.menu_Security.clicked.connect(lambda:self.ShowSecurity())
        self.menu_Security.move(300, 380)
        self.menu_Security.setFixedSize(100, 100)
        self.menu_Security.setFont(font_main)
        self.menu_Security.show()

        self.menu_log = QtGui.QPushButton('Log', self)
        self.menu_log.clicked.connect(lambda:self.ShowLog())
        self.menu_log.move(400, 380)
        self.menu_log.setFixedSize(100, 100)
        self.menu_log.setFont(font_main)
        self.menu_log.show()

        self.menu_exit = QtGui.QPushButton('Exit', self)
        self.menu_exit.clicked.connect(lambda:self.Exit())
        self.menu_exit.move(700, 380)
        self.menu_exit.setFixedSize(100, 100)
        self.menu_exit.setFont(font_main)
        self.menu_exit.show()

        #main window

        self.main_title = QtGui.QLabel("initializinginitializing", self)
        self.main_title.move(25, 25)
        self.main_title.setFont(font_med)
        self.main_title.show()

        self.main_temp = QtGui.QLabel(str(HVAC_TEMP) + '\xb0', self)
        self.main_temp.move(370, -50)
        self.main_temp.setFont(font_xlarge)
        self.main_temp.show()

        self.main_temp_outside_tag = QtGui.QLabel('Outside:', self)
        self.main_temp_outside_tag.move(25, 300)
        self.main_temp_outside_tag.setFont(font_med)
        self.main_temp_outside_tag.show()
        
        self.main_temp_outside = QtGui.QLabel("initializinginitializinginitializing", self)
        self.main_temp_outside.move(250, 300)
        self.main_temp_outside.setFont(font_med)
        self.main_temp_outside.show()
        
        self.main_hvac_status_tag = QtGui.QLabel('Status:', self)
        self.main_hvac_status_tag.move(25, 250)
        self.main_hvac_status_tag.setFont(font_med)
        self.main_hvac_status_tag.show()

        self.main_hvac_status = QtGui.QLabel("initializinginitializinginitializing", self)
        self.main_hvac_status.move(250, 250)
        self.main_hvac_status.setFont(font_med)
        self.main_hvac_status.show()

        #weather window

        self.weather_title = QtGui.QLabel('Weather Forcast', self)
        self.weather_title.move(25, 25)
        self.weather_title.setFont(font_med)
        self.weather_title.hide()
        
        self.weather_today_date = QtGui.QLabel("initializing", self)
        self.weather_today_date.move(25, 200)
        self.weather_today_date.setFont(font_main)
        self.weather_today_date.hide()

        self.weather_today_desc = QtGui.QLabel("initializing", self)
        self.weather_today_desc.move(25, 225)
        self.weather_today_desc.setFont(font_main)
        self.weather_today_desc.hide()

        self.weather_today_hilo = QtGui.QLabel("initializing", self)
        self.weather_today_hilo.move(25, 250)
        self.weather_today_hilo.setFont(font_main)
        self.weather_today_hilo.hide()

        self.weather_next1_date = QtGui.QLabel("initializing", self)
        self.weather_next1_date.move(150, 200)
        self.weather_next1_date.setFont(font_main)
        self.weather_next1_date.hide()

        self.weather_next1_desc = QtGui.QLabel("initializing", self)
        self.weather_next1_desc.move(150, 225)
        self.weather_next1_desc.setFont(font_main)
        self.weather_next1_desc.hide()

        self.weather_next1_hilo = QtGui.QLabel("initializing", self)
        self.weather_next1_hilo.move(150, 250)
        self.weather_next1_hilo.setFont(font_main)
        self.weather_next1_hilo.hide()

        self.weather_next2_date = QtGui.QLabel("initializing", self)
        self.weather_next2_date.move(275, 200)
        self.weather_next2_date.setFont(font_main)
        self.weather_next2_date.hide()

        self.weather_next2_desc = QtGui.QLabel("initializing", self)
        self.weather_next2_desc.move(275, 225)
        self.weather_next2_desc.setFont(font_main)
        self.weather_next2_desc.hide()

        self.weather_next2_hilo = QtGui.QLabel("initializing", self)
        self.weather_next2_hilo.move(275, 250)
        self.weather_next2_hilo.setFont(font_main)
        self.weather_next2_hilo.hide()

        self.weather_next3_date = QtGui.QLabel("initializing", self)
        self.weather_next3_date.move(400, 200)
        self.weather_next3_date.setFont(font_main)
        self.weather_next3_date.hide()

        self.weather_next3_desc = QtGui.QLabel("initializing", self)
        self.weather_next3_desc.move(400, 225)
        self.weather_next3_desc.setFont(font_main)
        self.weather_next3_desc.hide()

        self.weather_next3_hilo = QtGui.QLabel("initializing", self)
        self.weather_next3_hilo.move(400, 250)
        self.weather_next3_hilo.setFont(font_main)
        self.weather_next3_hilo.hide()

        self.weather_next4_date = QtGui.QLabel("initializing", self)
        self.weather_next4_date.move(525, 200)
        self.weather_next4_date.setFont(font_main)
        self.weather_next4_date.hide()

        self.weather_next4_desc = QtGui.QLabel("initializing", self)
        self.weather_next4_desc.move(525, 225)
        self.weather_next4_desc.setFont(font_main)
        self.weather_next4_desc.hide()

        self.weather_next4_hilo = QtGui.QLabel("initializing", self)
        self.weather_next4_hilo.move(525, 250)
        self.weather_next4_hilo.setFont(font_main)
        self.weather_next4_hilo.hide()

        self.weather_next5_date = QtGui.QLabel("initializing", self)
        self.weather_next5_date.move(650, 200)
        self.weather_next5_date.setFont(font_main)
        self.weather_next5_date.hide()

        self.weather_next5_desc = QtGui.QLabel("initializing", self)
        self.weather_next5_desc.move(650, 225)
        self.weather_next5_desc.setFont(font_main)
        self.weather_next5_desc.hide()

        self.weather_next5_hilo = QtGui.QLabel("initializing", self)
        self.weather_next5_hilo.move(650, 250)
        self.weather_next5_hilo.setFont(font_main)
        self.weather_next5_hilo.hide()
        
        #settings window

        self.settings_title = QtGui.QLabel('Settings', self)
        self.settings_title.move(25, 25)
        self.settings_title.setFont(font_med)
        self.settings_title.hide()

        self.hvac_cool = QtGui.QPushButton('A/C On/Off', self)
        self.hvac_cool.clicked.connect(lambda:self.SetCool())
        self.hvac_cool.move(25, 125)
        self.hvac_cool.setFixedSize(300, 100)
        self.hvac_cool.setFont(font_med)
        self.hvac_cool.setStyleSheet("QPushButton { color : blue; }");
        self.hvac_cool.hide()

        self.hvac_heat = QtGui.QPushButton('Heat On/Off', self)
        self.hvac_heat.clicked.connect(lambda:self.SetHeat())
        self.hvac_heat.move(25, 250)
        self.hvac_heat.setFixedSize(300, 100)
        self.hvac_heat.setFont(font_med)
        self.hvac_heat.setStyleSheet("QPushButton { color : red; }");
        self.hvac_heat.hide()

        self.hvac_setting_cool = QtGui.QLabel(str(TEMP_SETTING_COOL), self)
        self.hvac_setting_cool.move(525, 110)
        self.hvac_setting_cool.setFont(font_large)
        self.hvac_setting_cool.hide()
        
        self.hvac_cool_up = QtGui.QPushButton('+', self)
        self.hvac_cool_up.clicked.connect(lambda:self.SetCoolUp())
        self.hvac_cool_up.move(400, 125)
        self.hvac_cool_up.setFixedSize(100, 100)
        self.hvac_cool_up.setFont(font_med)
        self.hvac_cool_up.hide()

        self.hvac_cool_dn = QtGui.QPushButton('-', self)
        self.hvac_cool_dn.clicked.connect(lambda:self.SetCoolDn())
        self.hvac_cool_dn.move(650, 125)
        self.hvac_cool_dn.setFixedSize(100, 100)
        self.hvac_cool_dn.setFont(font_med)
        self.hvac_cool_dn.hide()

        self.hvac_setting_heat = QtGui.QLabel(str(TEMP_SETTING_HEAT), self)
        self.hvac_setting_heat.move(525, 235)
        self.hvac_setting_heat.setFont(font_large)
        self.hvac_setting_heat.hide()

        self.hvac_heat_up = QtGui.QPushButton('+', self)
        self.hvac_heat_up.clicked.connect(lambda:self.SetHeatUp())
        self.hvac_heat_up.move(400, 250)
        self.hvac_heat_up.setFixedSize(100, 100)
        self.hvac_heat_up.setFont(font_med)
        self.hvac_heat_up.hide()

        self.hvac_heat_dn = QtGui.QPushButton('-', self)
        self.hvac_heat_dn.clicked.connect(lambda:self.SetHeatDn())
        self.hvac_heat_dn.move(650, 250)
        self.hvac_heat_dn.setFixedSize(100, 100)
        self.hvac_heat_dn.setFont(font_med)
        self.hvac_heat_dn.hide()

        #security window

        self.security_title = QtGui.QLabel('Security', self)
        self.security_title.move(25, 25)
        self.security_title.setFont(font_med)
        self.security_title.hide()

        self.security_video = QtGui.QWidget(self)
        self.security_video.setFixedSize(400, 400)
        self.security_video.move(350,0)
        self.security_video.hide()

        self.security_instance = vlc.Instance()
        self.security_player = self.security_instance.media_player_new()
        self.security_media = self.security_instance.media_new('rtsp://pi:Remotepi123@192.168.1.200/Streaming/Channels/102')
        self.security_media.get_mrl()
        self.security_player.set_media(self.security_media)
        self.security_player.set_xwindow(self.security_video.winId())

        self.security_cam1 = QtGui.QPushButton('CAM 1', self)
        self.security_cam1.clicked.connect(lambda:self.SetIPC1())
        self.security_cam1.move(100, 100)
        self.security_cam1.setFixedSize(100, 100)
        self.security_cam1.setFont(font_main)
        self.security_cam1.hide()

        self.security_cam2 = QtGui.QPushButton('CAM 2', self)
        self.security_cam2.clicked.connect(lambda:self.SetIPC2())
        self.security_cam2.move(200, 100)
        self.security_cam2.setFixedSize(100, 100)
        self.security_cam2.setFont(font_main)
        self.security_cam2.hide()

        self.security_cam3 = QtGui.QPushButton('CAM 3', self)
        self.security_cam3.clicked.connect(lambda:self.SetIPC3())
        self.security_cam3.move(100, 200)
        self.security_cam3.setFixedSize(100, 100)
        self.security_cam3.setFont(font_main)
        self.security_cam3.hide()

        self.security_cam4 = QtGui.QPushButton('CAM 4', self)
        self.security_cam4.clicked.connect(lambda:self.SetIPC4())
        self.security_cam4.move(200, 200)
        self.security_cam4.setFixedSize(100, 100)
        self.security_cam4.setFont(font_main)
        self.security_cam4.hide()

        #log window

        self.log_window = QtGui.QLabel("initializinginitializinginitializinginitializinginitializing", self)
        self.log_window.move(25, 25)
        self.log_window.setFont(font_main)
        self.log_window.hide()

        self.log_refresh = QtGui.QPushButton('Refresh', self)
        self.log_refresh.clicked.connect(lambda:self.LogUpdate())
        self.log_refresh.move(700, 000)
        self.log_refresh.setFixedSize(100, 100)
        self.log_refresh.setFont(font_main)
        self.log_refresh.hide()

        #startup
        
        self.show()
        self.Log()
        self.Tweet()
        self.UpdateWeather()
        
    #functions for gui

    def ShowMain(self):
        self.HideWeather()
        self.HideSettings()
        self.HideSecurity()
        self.HideLog()
        self.main_title.show()
        self.main_temp.show()
        self.main_temp_outside.show()
        self.main_temp_outside_tag.show()
        self.main_hvac_status.show()
        self.main_hvac_status_tag.show()
        
    def HideMain(self):
        self.main_title.hide()
        self.main_temp.hide()
        self.main_temp_outside.hide()
        self.main_temp_outside_tag.hide()
        self.main_hvac_status.hide()
        self.main_hvac_status_tag.hide()

    def ShowWeather(self):
        self.HideMain()
        self.HideSettings()
        self.HideSecurity()
        self.HideLog()
        self.weather_title.show()
        self.weather_today_date.show()
        self.weather_today_desc.show()
        self.weather_today_hilo.show()
        self.weather_next1_date.show()
        self.weather_next1_desc.show()
        self.weather_next1_hilo.show()
        self.weather_next2_date.show()
        self.weather_next2_desc.show()
        self.weather_next2_hilo.show()
        self.weather_next3_date.show()
        self.weather_next3_desc.show()
        self.weather_next3_hilo.show()
        self.weather_next4_date.show()
        self.weather_next4_desc.show()
        self.weather_next4_hilo.show()
        self.weather_next5_date.show()
        self.weather_next5_desc.show()
        self.weather_next5_hilo.show()

    def HideWeather(self):
        self.weather_title.hide()
        self.weather_today_date.hide()
        self.weather_today_desc.hide()
        self.weather_today_hilo.hide()
        self.weather_next1_date.hide()
        self.weather_next1_desc.hide()
        self.weather_next1_hilo.hide()
        self.weather_next2_date.hide()
        self.weather_next2_desc.hide()
        self.weather_next2_hilo.hide()
        self.weather_next3_date.hide()
        self.weather_next3_desc.hide()
        self.weather_next3_hilo.hide()
        self.weather_next4_date.hide()
        self.weather_next4_desc.hide()
        self.weather_next4_hilo.hide()
        self.weather_next5_date.hide()
        self.weather_next5_desc.hide()
        self.weather_next5_hilo.hide()

    def ShowSettings(self):
        self.HideMain()
        self.HideWeather()
        self.HideSecurity()
        self.HideLog()
        self.settings_title.show()
        self.hvac_setting_cool.show()
        self.hvac_cool.show()
        self.hvac_cool_up.show()
        self.hvac_cool_dn.show()
        self.hvac_setting_heat.show()
        self.hvac_heat.show()
        self.hvac_heat_up.show()
        self.hvac_heat_dn.show()

    def HideSettings(self):
        self.settings_title.hide()
        self.hvac_setting_cool.hide()
        self.hvac_cool.hide()
        self.hvac_cool_up.hide()
        self.hvac_cool_dn.hide()
        self.hvac_setting_heat.hide()
        self.hvac_heat.hide()
        self.hvac_heat_up.hide()
        self.hvac_heat_dn.hide()

    def ShowSecurity(self):
        self.HideMain()
        self.HideWeather()
        self.HideSettings()
        self.HideLog()
        self.security_title.show()
        self.security_cam1.show()
        self.security_cam2.show()
        self.security_cam3.show()
        self.security_cam4.show()
        self.security_player.play()
        self.security_video.show()

    def HideSecurity(self):
        self.security_title.hide()
        self.security_player.stop()
        self.security_video.hide()
        self.security_cam1.hide()
        self.security_cam2.hide()
        self.security_cam3.hide()
        self.security_cam4.hide()

    def ShowLog(self):
        self.HideMain()
        self.HideWeather()
        self.HideSettings()
        self.HideSecurity()
        self.log_window.show()
        self.log_refresh.show()
        

    def HideLog(self):
        self.log_window.hide()
        self.log_refresh.hide()

    def Exit(self):
        sys.exit()

    #functions for settings

    def SetAuto(self):
        global HVAC_AUTO
        if (HVAC_AUTO == "on"):
            HVAC_AUTO = "off"
        else:
            HVAC_AUTO = "on"
        self.hvac_auto_setting.setText(HVAC_AUTO)

    def SetCool(self):
        global HVAC_COOL
        if (HVAC_COOL == "on"):
            HVAC_COOL = "off"
            self.hvac_cool.setStyleSheet("QPushButton { color : default; }");
        else:
            HVAC_COOL = "on"
            self.hvac_cool.setStyleSheet("QPushButton { color : blue; }");

    def SetHeat(self):
        global HVAC_HEAT
        if (HVAC_HEAT == "on"):
            HVAC_HEAT = "off"
            self.hvac_heat.setStyleSheet("QPushButton { color : default; }");
        else:
            HVAC_HEAT = "on"
            self.hvac_heat.setStyleSheet("QPushButton { color : red; }");

    def SetCoolUp(self):
        global TEMP_SETTING_COOL
        global TEMP_SETTING_HEAT
        TEMP_SETTING_COOL = TEMP_SETTING_COOL + 1
        self.hvac_setting_cool.setText(str(TEMP_SETTING_COOL))

    def SetCoolDn(self):
        global TEMP_SETTING_COOL
        global TEMP_SETTING_HEAT
        TEMP_SETTING_COOL = TEMP_SETTING_COOL - 1
        if (TEMP_SETTING_COOL < (TEMP_SETTING_HEAT + 6)):
            TEMP_SETTING_HEAT = TEMP_SETTING_HEAT -1
        self.hvac_setting_cool.setText(str(TEMP_SETTING_COOL))
        self.hvac_setting_heat.setText(str(TEMP_SETTING_HEAT))

    def SetHeatUp(self):
        global TEMP_SETTING_COOL
        global TEMP_SETTING_HEAT
        TEMP_SETTING_HEAT = TEMP_SETTING_HEAT + 1
        if (TEMP_SETTING_COOL < (TEMP_SETTING_HEAT + 6)):
            TEMP_SETTING_COOL = TEMP_SETTING_COOL + 1
        self.hvac_setting_cool.setText(str(TEMP_SETTING_COOL))
        self.hvac_setting_heat.setText(str(TEMP_SETTING_HEAT))

    def SetHeatDn(self):
        global TEMP_SETTING_COOL
        global TEMP_SETTING_HEAT
        TEMP_SETTING_HEAT = TEMP_SETTING_HEAT - 1
        self.hvac_setting_heat.setText(str(TEMP_SETTING_HEAT))

    #functions for security

    def SetIPC1(self):
        self.security_media = self.security_instance.media_new('rtsp://pi:Remotepi123@192.168.1.200/Streaming/Channels/102')
        self.RestartVideo()

    def SetIPC2(self):
        self.security_media = self.security_instance.media_new('rtsp://pi:Remotepi123@192.168.1.200/Streaming/Channels/202')
        self.RestartVideo()

    def SetIPC3(self):
        self.security_media = self.security_instance.media_new('rtsp://pi:Remotepi123@192.168.1.200/Streaming/Channels/302')
        self.RestartVideo()

    def SetIPC4(self):
        self.security_media = self.security_instance.media_new('rtsp://pi:Remotepi123@192.168.1.200/Streaming/Channels/402')
        self.RestartVideo()
    
    def RestartVideo(self):
        self.security_media.get_mrl()
        self.security_player.set_media(self.security_media)
        self.security_player.set_xwindow(self.security_video.winId())
        self.security_player.stop()
        self.security_player.play()

    #functions for log

    def LogUpdate(self):
        print("syslog read")
        #print(sys.stdin.readline())

        #self.log_window.setText(sys.stdin.readline())

    #functions misc

    def SetConfig(self):
        try:
            log = open("/ramtmp/hvac.config","w")
            log.write(str(HVAC_COOL) + "\n")
            log.write(str(HVAC_HEAT) + "\n")
            log.write(str(TEMP_SETTING_COOL) + "\n")
            log.write(str(TEMP_SETTING_HEAT) + "\n")
            log.close()
        except:
            print(" ********** WRITE FAILED **********")

    def GetConfig(self):
        global HVAC_TEMP
        global HVAC_STATUS
        try:
            log = open("/ramtmp/hvac.output","r")
            str1 = log.readline().rstrip('\r\n')
            HVAC_TEMP = int(float(str1))
            HVAC_STATUS = log.readline().rstrip('\r\n')
            log.close()
        except:
            print(" ********** READ FAILED  **********")
            HVAC_STATUS = "error"
            HVAC_TEMP = 999

    def Update(self):
        self.SetConfig()
        self.GetConfig()
        self.main_temp.setText(str(HVAC_TEMP) + '\xb0')
        self.main_hvac_status.setText(HVAC_STATUS)

    def Tweet(self):
        global HVAC_COOL
        global HVAC_HEAT
        global HVAC_STATUS
        global HVAC_TEMP
        t = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        s = str(t + "\t CFG: " + str(HVAC_COOL) + " " + str(HVAC_HEAT) + "\t HVAC: " + str(HVAC_STATUS) + "\t THRM: " + str(HVAC_TEMP))
        try:
            TWEET.update_status(status = s)
            print(t + " ********** TWEET        **********")
        except:
            print(t + " ********** TWEET FAILED **********")

    def Log(self):
        global HVAC_COOL
        global HVAC_HEAT
        global HVAC_STATUS
        global HVAC_TEMP
        t = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        s = str(t + "\t CFG: " + str(HVAC_COOL) + " " + str(HVAC_HEAT) + "\t HVAC: " + str(HVAC_STATUS) + "\t THRM: " + str(HVAC_TEMP))
        print(s)

    def UpdateWeather(self):
        t = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        print(t + " ********** READ WEATHER **********")
        
        weather = Weather()
        location = weather.lookup_by_location('chickasha')
        forecasts = location.forecast()
        
        WEATHER_TODAY_HI = forecasts[0].high()
        WEATHER_TODAY_LO = forecasts[0].low()
        WEATHER_TODAY_DESC = forecasts[0].text()
        WEATHER_TODAY_DATE = forecasts[0].date()
        WEATHER_NEXT1_HI = forecasts[1].high()
        WEATHER_NEXT1_LO = forecasts[1].low()
        WEATHER_NEXT1_DESC = forecasts[1].text()
        WEATHER_NEXT1_DATE = forecasts[1].date()
        WEATHER_NEXT2_HI = forecasts[2].high()
        WEATHER_NEXT2_LO = forecasts[2].low()
        WEATHER_NEXT2_DESC = forecasts[2].text()
        WEATHER_NEXT2_DATE = forecasts[2].date()
        WEATHER_NEXT3_HI = forecasts[3].high()
        WEATHER_NEXT3_LO = forecasts[3].low()
        WEATHER_NEXT3_DESC = forecasts[3].text()
        WEATHER_NEXT3_DATE = forecasts[3].date()
        WEATHER_NEXT4_HI = forecasts[4].high()
        WEATHER_NEXT4_LO = forecasts[4].low()
        WEATHER_NEXT4_DESC = forecasts[4].text()
        WEATHER_NEXT4_DATE = forecasts[4].date()
        WEATHER_NEXT5_HI = forecasts[5].high()
        WEATHER_NEXT5_LO = forecasts[5].low()
        WEATHER_NEXT5_DESC = forecasts[5].text()
        WEATHER_NEXT5_DATE = forecasts[5].date()
        WEATHER_NEXT6_HI = forecasts[6].high()
        WEATHER_NEXT6_LO = forecasts[6].low()
        WEATHER_NEXT6_DESC = forecasts[6].text()
        WEATHER_NEXT6_DATE = forecasts[6].date()

        self.main_title.setText(str(WEATHER_TODAY_DATE))
        self.main_temp_outside.setText(str(WEATHER_TODAY_DESC) + "  " + str(WEATHER_TODAY_HI) + '\xb0' + " / " + str(WEATHER_TODAY_LO) + '\xb0')
        self.weather_today_date.setText(str(WEATHER_TODAY_DATE))
        self.weather_today_desc.setText(str(WEATHER_TODAY_DESC))
        self.weather_today_hilo.setText(str(WEATHER_TODAY_HI) + '\xb0' + " / " + str(WEATHER_TODAY_LO) + '\xb0')
        self.weather_next1_date.setText(str(WEATHER_NEXT1_DATE))
        self.weather_next1_desc.setText(str(WEATHER_NEXT1_DESC))
        self.weather_next1_hilo.setText(str(WEATHER_NEXT1_HI) + '\xb0' + " / " + str(WEATHER_NEXT1_LO) + '\xb0')
        self.weather_next2_date.setText(str(WEATHER_NEXT2_DATE))
        self.weather_next2_desc.setText(str(WEATHER_NEXT2_DESC))
        self.weather_next2_hilo.setText(str(WEATHER_NEXT2_HI) + '\xb0' + " / " + str(WEATHER_NEXT2_LO) + '\xb0')
        self.weather_next3_date.setText(str(WEATHER_NEXT3_DATE))
        self.weather_next3_desc.setText(str(WEATHER_NEXT3_DESC))
        self.weather_next3_hilo.setText(str(WEATHER_NEXT3_HI) + '\xb0' + " / " + str(WEATHER_NEXT3_LO) + '\xb0')
        self.weather_next4_date.setText(str(WEATHER_NEXT4_DATE))
        self.weather_next4_desc.setText(str(WEATHER_NEXT4_DESC))
        self.weather_next4_hilo.setText(str(WEATHER_NEXT4_HI) + '\xb0' + " / " + str(WEATHER_NEXT4_LO) + '\xb0')
        self.weather_next5_date.setText(str(WEATHER_NEXT5_DATE))
        self.weather_next5_desc.setText(str(WEATHER_NEXT5_DESC))
        self.weather_next5_hilo.setText(str(WEATHER_NEXT5_HI) + '\xb0' + " / " + str(WEATHER_NEXT5_LO) + '\xb0')

#===========================================================================================
#main

def main():

    app = QtGui.QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
