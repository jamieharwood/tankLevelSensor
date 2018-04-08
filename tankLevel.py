from machine import Pin
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii

level1Pin = Pin(4, Pin.IN, Pin.PULL_UP)  # D3
level2Pin = Pin(0, Pin.IN, Pin.PULL_UP)  # D4
level3Pin = Pin(5, Pin.IN, Pin.PULL_UP)  # D4

numSensors = 3

neoLow = 0
neoMid = 64
neoHi = 255

functionStateChanged = False


def main():
    vars.levels = [level1Pin.value(), level2Pin.value(), level3Pin.value()]

    # Set initial state
    np = neopixel.NeoPixel(machine.Pin(12), 4)

    np[3] = (neoMid, neoLow, neoLow)

    for sensor in range(0, numSensors):
        if vars.levels[sensor]:
            np[sensor] = (neoMid, neoLow, neoMid)
        else:
            np[sensor] = (neoLow, neoMid, neoLow)

    np.write()

    sensorValueLast = 0

    while True:
        # Read switch inputs
        vars.levels = [level1Pin.value(), level2Pin.value(), level3Pin.value()]
        functionStateChanged = False
        sensorValue = 0

        for sensor in range(0, numSensors):  # Count the high inputs.
            # Check against the last input
            if vars.levels[sensor] == 0:
                sensorValue += 1

        for sensor in range(0, numSensors):  # reset to low.
            np[sensor] = (neoMid, neoLow, neoMid)

        for sensor in range(0, sensorValue):  # Set actual value.
            np[sensor] = (neoLow, neoMid, neoLow)

        np.write()

        if sensorValue != sensorValueLast:  # Has the tank state changed?
            functionStateChanged = True
            sensorValueLast = sensorValue

        if functionStateChanged:  # State changed, store the new level.

            deviceid = ubinascii.hexlify(machine.unique_id()).decode()
            deviceid = deviceid.replace('b\'', '')
            deviceid = deviceid.replace('\'', '')

            url = "http://192.168.86.240:5000/sensorStateWrite/{0}/{1}/{2}"
            url = url.replace('{0}', deviceid)  # sensor id
            url = url.replace('{1}', 'level')  # sensor type
            url = url.replace('{2}', str(sensorValue))  # sensor value

            print(url)

            try:
                response = urequests.get(url)

                # print(url)
                print(response.text)

                # utime.sleep(0.25)

                response.close()
            except:
                print('Fail www connect...')


main()
