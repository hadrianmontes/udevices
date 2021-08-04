import time
from bluepy.btle import Scanner, Peripheral

scan = Scanner()

found = False

while not found:
    devices = scan.scan()
    for device in devices:
        try:
            if device.getScanData()[1][-1] == "uweather":
                uweather= device
                found = True
                print("Device Found")
                break
        except IndexError:
            continue
    else:
        print("Device not found Retrying")
uweather = Peripheral(uweather.addr)
uweather.connect(uweather.addr)
for service in uweather.getServices():
    service_weather = service

while True:
    time.sleep(10)
    characteristics = service_weather.getCharacteristics()
    print("Temperature {}".format(characteristics[0].read()))

