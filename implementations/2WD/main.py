import socket_blink
import machine
import time
import json
import twowd

LED_PIN = 22
LED_ON = 0
LED = machine.Pin(LED_PIN, machine.Pin.OUT)
time.sleep(5)
socket = socket_blink.Socket("192.168.4.1", 123, LED)

two_wheel = twowd.two_wheel_drive_from_pins((16, 17, 18), (25, 26, 27), timer=1)
while True:
    socket.wait_for_connection()
    while socket.conexion is not None:
        data = socket.read()
        if data is None:
            print("Disconected")
        elif len(data) == 0:
            pass
        else:
            info = data.split("\n")[-1]
            joystick = json.loads(info)
            print(info)
            two_wheel.set_from_joystick(joystick)
        time.sleep(1/30)
socket.led(not socket.LED_ON)