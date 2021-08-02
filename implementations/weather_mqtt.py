from umqtt.simple import MQTTClient
import machine
import time
import json
from bme280 import BME280

def meassure():
    bme = BME280(i2c=machine.I2C(0))
    bme.update()
    info = {"temperature": bme.temperature, "pressure": bme.pressure}
    return info

WAIT_TIME = 300000
time.sleep(1)
out = machine.Pin(16, machine.Pin.OUT)
out(0)
inp = machine.Pin(13, machine.Pin.IN)
if not inp():
    try:
        info = meassure()
        message = json.dumps(info).encode()
        topic = b"weather/outside"
    except:
        message = b"Error cargando BME280 en Terraza"
        topic = b"ERRORS"
    print(message)
    
    try:
        print("Connecting Client")
        KEEP_ALIVE = int(2.2*WAIT_TIME/1000)
        c = MQTTClient("umqtt_client", "192.168.1.85", user="admin", password="24111993", keepalive=KEEP_ALIVE)
        c.set_last_will(b"ERRORS", b"Sensor BME280 en terraza desconectado")
        c.connect()
        c.publish(topic, message)
        time.sleep(2)
        c.disconnect()
        print("Disconeecting Client")
    except:
        print("Error in Conexion")
        time.sleep(2)
else:
    print("Charging")
machine.deepsleep(WAIT_TIME)

