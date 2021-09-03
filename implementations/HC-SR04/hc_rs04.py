import machine
import time

class HC_SR04:
    
    _SPEED_OF_SOUND = 343 * 1E3 / 1E6  # 343 m/s -> mm/us
    MAX_MEASSURE_DISTANCE = 4000  # 4 m in mm
    
    def __init__(self, trigger_pin, echo_pin):
        self._trigger = trigger_pin
        self._echo = echo_pin
        
        self._distance = None
    
    def meassure_distance(self, repetitions=1):
        self._distance = None
        distances = [self._meassure_one() for _ in range(repetitions)]
        distances = [i for i in distances if distances > 1]
        
        if len(distances) > 0:
            self._distance = sum(distances) / len(distances)
        else:
            self._distance = -1
    
    def _meassure_one(self):
        # Time to meassure the maximum distance (times 2)
        timeout = int(self._SPEED_OF_SOUND * self.MAX_MEASSURE_DISTANCE * 2)
        self._trigger(0)
        time.sleep_us(5)
        self._trigger(1)
        time.sleep_us(10)
        try:
            pulse = machine.time_pulse_us(self._echo, 1, timeout)
        except OSError:
            pulse = -1
        return pulse * self._SPEED_OF_SOUND // 2
    
    @property
    def distance(self):
        return self._distance
        
    @classmethod
    def from_pin_numbers(cls, trigger, echo):
        trigger_pin = machine.Pin(trigger, machine.Pin.OUT)
        echo_pin = machine.Pin(echo, machine.Pin.IN)
        return cls(trigger_pin, echo_pin)