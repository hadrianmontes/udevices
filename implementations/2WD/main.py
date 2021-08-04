import socket_blink
import machine
import time
import twowd

LED_PIN = 22
LED_ON = 0
LED = machine.Pin(LED_PIN, machine.Pin.OUT)
time.sleep(5)
socket = socket_blink.Socket("192.168.1.44", 123, LED)

motor = twowd.motor_from_pins(16, 17, 18)

while True:
    socket.wait_for_connection()
    while socket.conexion is not None:
        data = socket.read()
        if data is None:
            print("Disconected")
        elif len(data) == 0:
            pass
        else:
            print(data)
            motor.set_velocity(float(data))
        time.sleep(1)
socket.led(not socket.LED_ON)