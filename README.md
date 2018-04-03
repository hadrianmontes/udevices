# udevices
A series of simple devices to be controlled using MicroPython.

This is a brother proyect of https://github.com/hadrianmontes/raspberry_diy_devices but compatible with micropython.

This module implements several classes to
interact with diferent sensors/devices conected to a micropython device (these ones are tested with the esp32).
Each device is impleneted in a separate file and independent from the
others (unless specified for some classes). The classes implemented
right now are:

  * Shift Register: A simple N bit shift register that can be chained to create bigger register.
    * File: [shift_register.py](./udevices/shift_register.py)
    * Fle Dependency: None
    * Status: Working
  * BME280 & BMP280: A temperature, pressure (and humidity) sensor conected by **I2C**.
    * File: [bme280.py](./udevices/bme280.py)
	* File Dependency: None
	* Status: Works for temperature and pressure and in the forced (manual) mode.

