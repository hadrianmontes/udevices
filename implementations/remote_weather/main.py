from bme280 import BME280
import bluetooth
import utime

INTERVAL = 10
SDA = 15
SCL = 4
temperature_char = bluetooth.Characteristic(uuid=1, flags=bluetooth.FLAG_READ)
pressure_char = bluetooth.Characteristic(uuid=2, flags=bluetooth.FLAG_READ)
blue = bluetooth.Bluetooth()
blue.active(True)
blue.advertise(100, "uweather")
blue.add_service(uuid=1, characteristics=[temperature_char, pressure_char])

sensor = BME280(sda=SDA, scl=SCL)

while True:
    sensor.update()
    temperature_char.write(str(sensor.temperature))
    pressure_char.write(str(sensor.pressure))
    utime.sleep(INTERVAL)
    
