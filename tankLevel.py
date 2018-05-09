#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankLevel
"""

from machine import RTC
from machine import Pin
import network
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii
from heartbeatClass import HeartBeat
from timeClass import TimeTank
from SensorRegistationClass import SensorRegistation

level1Pin = Pin(4, Pin.IN, Pin.PULL_UP)  # D3
level2Pin = Pin(0, Pin.IN, Pin.PULL_UP)  # D4
level3Pin = Pin(5, Pin.IN, Pin.PULL_UP)  # D4

numSensors = 3

np = neopixel.NeoPixel(Pin(12), 4)
neoLow = 0
neoMid = 64
neoHi = 255

red = (neoMid, neoLow, neoLow)
yellow = (255, 226, neoLow)
tango = (243, 114, 82)
green = (neoLow, neoMid, neoLow)
indigo = (neoLow, 126, 135)
blue = (neoLow, neoLow, neoMid)
purple = (neoMid, neoLow, neoMid)
black = (neoLow, neoLow, neoLow)

powerLed = 3
level1 = 2
level2 = 1
level3 = 0

# Set initial state
np[powerLed] = red
np[level1] = purple
np[level2] = purple
np[level3] = purple
np.write()


def getdeviceid():
    deviceid = ubinascii.hexlify(machine.unique_id()).decode()
    deviceid = deviceid.replace('b\'', '')
    deviceid = deviceid.replace('\'', '')

    return deviceid


def getip():
    sta_if = network.WLAN(network.STA_IF)
    temp = sta_if.ifconfig()

    return temp[0]


def testfornetwork():
    sta_if = network.WLAN(network.STA_IF)
    while not sta_if.active():
        print('Waiting for Wifi')

    while '0.0.0.0' == getip():
        print('Waiting for IP')


def main():
    testfornetwork()

    debug = False
    sensorname = 'level'

    if debug:
        sensorname += '-debug'

    deviceid = getdeviceid()

    mySensorRegistation = SensorRegistation(deviceid)
    mySensorRegistation.register(sensorname, 'Hardware', 'JH')

    myheartbeat = HeartBeat(deviceid)
    myheartbeat.beat()

    mytime = TimeTank(deviceid)
    mytime.settime(1)

    rtc = RTC()
    sampletimes = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
    samplehours = [1, 6, 12, 18]
    isMinuteProcess = 0
    lastMin = 0
    gethour = 0

    vars.levels = [level1Pin.value(), level2Pin.value(), level3Pin.value()]
    sensorValueLast = 0

    # Set initial state
    for sensor in range(0, numSensors):
        if vars.levels[sensor]:
            np[sensor] = purple
        else:
            np[sensor] = green

    np.write()

    while True:
        timeNow = rtc.datetime()
        currHour = timeNow[4]
        currMinute = timeNow[5]

        if currMinute not in sampletimes and isMinuteProcess == 0:
            # process goes here

            isMinuteProcess = 1

        if currMinute in sampletimes and isMinuteProcess == 1:
            # process goes here

            isMinuteProcess = 0

        if lastMin != currMinute:
            # process goes here
            myheartbeat.beat()

            lastMin = currMinute

        if currHour not in samplehours and gethour == 0:
            gethour = 1

        if currHour in samplehours and gethour == 1:
            gethour = 0
            local = utime.localtime()
            mytime.settime(1)

        # Read switch inputs
        vars.levels = [level1Pin.value(), level2Pin.value(), level3Pin.value()]
        functionStateChanged = False
        sensorValue = 0

        for sensor in range(0, numSensors):  # Count the high inputs.
            # Check against the last input
            if vars.levels[sensor] == 0:
                sensorValue += 1

        for sensor in range(0, numSensors):  # reset to low.
            np[sensor] = purple

        for sensor in range(0, sensorValue):  # Set actual value.
            np[sensor] = green

        np.write()

        if sensorValue != sensorValueLast:  # Has the tank state changed?
            functionStateChanged = True
            sensorValueLast = sensorValue

        if functionStateChanged:  # State changed, store the new level.

            url = "http://192.168.86.240:5000/sensorStateWrite/{0}/{1}/{2}"
            url = url.replace('{0}', deviceid)  # sensor id
            url = url.replace('{1}', sensorname)  # sensor type
            url = url.replace('{2}', str(sensorValue))  # sensor value

            print(url)

            try:
                response = urequests.get(url)

                print(response.text)

                response.close()
            except:
                print('Fail www connect...')


main()

