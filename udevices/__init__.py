from .bme280 import BME280
from .shift_register import ShiftRegister
from .storage import Deque, MultipleHistorial

def OLED():
    """
    Wrapper to load an integrated ssd1306 screen
    """
    import machine
    from udevices import ssd1306
    i2c = machine.I2C(scl=machine.Pin(4), sda=machine.Pin(5))
    return ssd1306.SSD1306_I2C(128, 64, i2c)
    

__all__ = ("BME280", "ShiftRegister", "Deque", "MultipleHistorial")
