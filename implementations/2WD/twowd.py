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
        duty = int(abs(velocity) * self.MAX_DUTY)
        print(duty)
        self.pin_enable.duty(duty)
        self._current_velocity = velocity
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

class TwoWheelDrive:
    DEFAULT_TIMEOUT = 500
    def __init__(self, right_motor: Motor, left_motor: Motor, timer: int = None):
        self.right_motor = right_motor
        self.left_motor = left_motor
        
        if timer is not None:
            self.timer = machine.Timer(timer)
        else:
            self.timer = None
            
        self._speed = 0
        self._direction = (0, 0)
        
    def set_velocity(self, speed, direction, timeout=None):
        stop = lambda _: self.stop()
        if speed > 1:
            raise ValueError("Speed must be between 0 and 1")
        
        self._speed = speed
        self._direction = direction
        
        left = direction[0] + direction[1]
        right = direction[0] - direction[1]
        maxi = max((abs(left), abs(right)))
        if maxi == 0:
            maxi = 1
        left *= speed/maxi
        right *= speed/maxi
        print(left, right)
        self.left_motor.set_velocity(left)
        self.right_motor.set_velocity(right)
        
        if self.timer is not None:
            self.timer.deinit()
            timeout = self.DEFAULT_TIMEOUT if timeout is None else timeout
            self.timer.init(mode=machine.Timer.ONE_SHOT,
                            period=timeout,
                            callback=stop)
    
    def set_from_joystick(self, direction, timeout=None):
        speed = min((direction[0]**2 + direction[1]**2, 1))
        self.set_velocity(speed, direction, timeout=timeout)
            
    def stop(self):
        if self.timer:
            self.timer.deinit
        self.left_motor.stop()
        self.right_motor.stop()        
        
def two_wheel_drive_from_pins(right_pins, left_pins, timer=None):
    left = motor_from_pins(*left_pins)
    right = motor_from_pins(*right_pins)
    two_wheel = TwoWheelDrive(right, left, timer=timer)
    return two_wheel