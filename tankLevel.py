from machine import Pin
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii

level1Pin = Pin(4, Pin.IN, Pin.PULL_UP)  # D3
level2Pin = Pin(0, Pin.IN, Pin.PULL_UP)  # D4
level3Pin = Pin(14, Pin.IN, Pin.PULL_UP)  # D4
neoMid = 64
neoHi = 255

functionStateChanged = False


def main():
    np = neopixel.NeoPixel(machine.Pin(12), 4)

    # Set initial state
    np[0] = (255, 0, 0)
    np[1] = (neoMid, 0, neoMid)
    np[2] = (neoMid, 0, neoMid)
    np[3] = (neoMid, 0, neoMid)
    np.write()

    vars.levels = [level1Pin.value(), level2Pin.value(), level3Pin.value()]

    if vars.levels[0]:
        np[1] = (neoMid, 0, neoMid)
    else:
        np[1] = (0, neoHi, 0)

    if vars.levels[1]:
        np[2] = (neoMid, 0, neoMid)
    else:
        np[2] = (0, neoHi, 0)

    if vars.levels[2]:
        np[3] = (neoMid, 0, neoMid)
    else:
        np[3] = (0, neoHi, 0)

    np.write()

    while True:
        # Read switch inputs
        vars.levels = [level1Pin.value(), level2Pin.value(), level3Pin.value()]
        functionStateChanged = False
        sensorValue = 0

        for sensor in range(0, 3):
            # Check against the last input
            if vars.levels[sensor] != vars.levelsLast[sensor]:
                if vars.levels[sensor]:
                    np[sensor + 1] = (neoMid, 0, neoMid)
                else:
                    np[sensor + 1] = (0, neoHi, 0)

                np.write()
                functionStateChanged = True

                vars.levelsLast = vars.levels  # Set the last pointers
                print('if ( vars.levelsLast != vars.level ):')

            if functionStateChanged:

                deviceid = ubinascii.hexlify(machine.unique_id()).decode()
                deviceid = deviceid.replace('b\'', '')
                deviceid = deviceid.replace('\'', '')

                url = "http://192.168.86.240:5000/sensorStateWrite/{0}/{1}/{2}"
                url = url.replace('{0}', deviceid)  # sensor id
                url = url.replace('{1}', 'level-{0}'.replace('{0}', str(sensor)))  # sensor type
                url = url.replace('{2}', str(vars.levels[sensor]))  # sensor value

                print(url)

                try:
                    response = urequests.get(url)

                    # print(url)
                    print(response.text)

                    # utime.sleep(0.25)

                    response.close()
                except:
                    print('Fail www connect...')

            functionStateChanged = False

        np.write()


main()
