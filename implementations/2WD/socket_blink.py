import time
import usocket
import machine

class Socket():
    LED_ON = 0
    PERIOD = 500
    def __init__(self, ip, port, led, timer=0):
        self.sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(1)
        self.timer = machine.Timer(timer)
        self.led = led
        self.led(not self.LED_ON)
        
        self.conexion = None
        
    def start_blink(self):
        toggle = lambda _: self.led(not self.led.value())
        self.timer.deinit()
        self.timer.init(mode=machine.Timer.PERIODIC,
                        period=self.PERIOD,
                        callback=toggle)
    
    def stop_blink(self):
        self.timer.deinit()
        time.sleep_ms(self.PERIOD)
        self.led(self.LED_ON)
    
    def wait_for_connection(self):
        self.start_blink()
        self.conexion, _ = self.sock.accept()
        self.conexion.setblocking(False)
        self.stop_blink()
        
    def read(self, *args, **kwargs):
        if self.conexion is None:
            return None    
        data = self.conexion.read(*args, **kwargs)
        if data is None:
            return ""
        elif len(data) == 0:
            self.conexion = None
            self.start_blink()
            return None
        else:
            return data.decode()