import time
import machine

class Motor:
    FORWARD = 1
    STOP = 0
    BACKWARDS = -1
    
    MAX_DUTY = 1023
    def __init__(self, pin_enable: machine.Pin,
                 pin_fwd: machine.Pin, pin_bwd: machine.Pin):
        self.pin_enable = pin_enable
        self.pin_fwd = pin_fwd
        self.pin_bwd = pin_bwd
        
        self._current_velocity = 0 
        self._current_direction = 0
        
        self.stop()
        
    def set_velocity(self, velocity):
        if abs(velocity) > 1:
            raise ValueError("Velocity must be between -1 and 1")
        duty = int(abs(velocity) * 1024)
        self.pin_enable.duty(duty)
        self._set_direction(self._find_direction(velocity))
        
    def stop(self):
        self.set_velocity(0)
        
    def _set_direction(self, direction):
        if self._current_direction == direction:
            return
        elif direction == self.FORWARD:
            self.pin_bwd(0)
            self.pin_fwd(1)
        elif direction == self.BACKWARDS:
            self.pin_fwd(0)
            self.pin_bwd(1)
        elif direction == self.STOP:
            self.pin_fwd(0)
            self.pin_bwd(0)
        self._current_direction = direction
            
    @classmethod
    def _find_direction(cls, velocity):
        if velocity == 0:
            return cls.STOP
        elif velocity > 0:
            return cls.FORWARD
        elif velocity < 0:
            return cls.BACKWARDS
        
        
    
    @property
    def current_velocity(self):
        # type: () -> float
        return self._current_velocity

def motor_from_pins(num_enable: int, num_fwd: int, num_bwd: int):
    enable = machine.Pin(num_enable)
    pin_enable = machine.PWM(enable)
    pin_fwd = machine.Pin(num_fwd, machine.Pin.OUT)
    pin_bwd = machine.Pin(num_bwd, machine.Pin.OUT)
    
    return Motor(pin_enable, pin_fwd, pin_bwd)