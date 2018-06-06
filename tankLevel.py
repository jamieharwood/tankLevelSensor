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
# import varibles as vars
import urequests
import ubinascii
from heartbeatClass import HeartBeat
from timeClass import TimeTank
from SensorRegistationClass import SensorRegistation
from NeoPixelClass import NeoPixel
from LogClass import Log

__log = Log()

__restHost = "http://192.168.86.240:5000"

__sensorname = ''
__deviceid = ''

__level1Pin = Pin(4, Pin.IN, Pin.PULL_UP)  # D3
__level2Pin = Pin(0, Pin.IN, Pin.PULL_UP)  # D4
__level3Pin = Pin(5, Pin.IN, Pin.PULL_UP)  # D4
__numSensors = 3
__levels = [0, 0, 0]

__neoPin = 12

__np = NeoPixel(__neoPin, 4)

powerLed = 3
level1 = 2
level2 = 1
level3 = 0

# Set initial state
__np.colour(powerLed, 'red')
__np.colour(level1, 'purple')
__np.colour(level2, 'purple')
__np.colour(level3, 'purple')
__np.write()

__debugcode = False


def printd(debugtext):
    if __debugcode:
        print(debugtext)


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
        printd('Waiting for Wifi')

    while '0.0.0.0' == getip():
        printd('Waiting for IP')

def settime(mytime):
    timecount = 0

    while not mytime.settime(1):
        timecount += 1

        if timecount > 10:
            machine.reset()


def main():
    global __levels, __deviceid, __sensorname, __log

    debug = False
    __sensorname = 'level'
    __deviceid = getdeviceid()

    if debug:
        __sensorname += "-" + __deviceid + '-debug'

    __log = Log(__restHost, __deviceid)

    testfornetwork()
    __log.printl('Test for network.')

    __log.printl('startup: tankLevel v1: ' + __sensorname)

    mySensorRegistation = SensorRegistation(__restHost, __deviceid)
    mySensorRegistation.register(__sensorname, 'Hardware', 'JH')
    __log.printl('registered: mySensorRegistation.register')

    myheartbeat = HeartBeat(__restHost, __deviceid)
    myheartbeat.beat()
    __log.printl('registered: myheartbeat.longbeat')

    mytime = TimeTank(__deviceid, __log.printl)
    settime(mytime)
    __log.printl('registered: mytime.settime')

    rtc = RTC()
    sampletimes = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
    samplehours = [1, 6, 12, 18]
    isMinuteProcess = 0
    lastMin = 0
    gethour = 0

    __levels = [__level1Pin.value(), __level2Pin.value(), __level3Pin.value()]
    sensorValueLast = -1

    # Set initial state
    for sensor in range(0, __numSensors):
        if __levels[sensor]:
            __np.colour(sensor, 'purple')
        else:
            __np.colour(sensor, 'green')

    __np.write()

    while True:
        timeNow = rtc.datetime()
        currHour = timeNow[4]
        currMinute = timeNow[5]

        if currMinute not in sampletimes and isMinuteProcess == 0:
            isMinuteProcess = 1
            # process goes here

        if currMinute in sampletimes and isMinuteProcess == 1:
            isMinuteProcess = 0
            __log.printl('sample times functions')
            # process goes here

        if lastMin != currMinute:
            lastMin = currMinute
            __log.printl('Minute functions')
            # process goes here

            myheartbeat.longbeat()
            __log.printl('Minute functions: myheartbeat.longbeat')

        if currHour not in samplehours and gethour == 0:
            gethour = 1
            # process goes here

        if currHour in samplehours and gethour == 1:
            gethour = 0
            __log.printl('Sample hour functions')
            # process goes here

            settime(mytime)
            local = utime.localtime()
            __log.printl('Sample hour functions: mytime.settime')

        # Read switch inputs
        __levels = [__level1Pin.value(), __level2Pin.value(), __level3Pin.value()]
        functionStateChanged = False
        sensorValue = 0

        for sensor in range(0, __numSensors):  # Count the high inputs.
            # Check against the last input
            if __levels[sensor] == 0:
                sensorValue += 1

        for sensor in range(0, __numSensors):  # reset to low.
            __np.colour(sensor, 'purple')

        for sensor in range(0, sensorValue):  # Set actual value.
            __np.colour(sensor, 'green')

        __np.write()

        if sensorValue != sensorValueLast:  # Has the tank state changed?
            functionStateChanged = True
            if sensorValueLast != -1:
                leveltext = 'Level changed: {0} to {1}'.replace('{0}', str(sensorValueLast))
                leveltext = leveltext.replace('{1}', str(sensorValue))

                __log.printl(leveltext)
            sensorValueLast = sensorValue

        if functionStateChanged:  # State changed, store the new level.

            url = __restHost + "/sensorStateWrite/{0}/{1}/{2}"
            url = url.replace('{0}', __deviceid)  # sensor id
            url = url.replace('{1}', __sensorname)  # sensor type
            url = url.replace('{2}', str(sensorValue))  # sensor value

            printd(url)

            try:
                response = urequests.get(url)

                printd(response.text)

                response.close()
            except:
                printd('Fail www connect...')


main()

