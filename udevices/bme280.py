import time
from machine import I2C, Pin
import struct

class BME280(object):

    DEFAULT_ADDRESS = 0x76
    REGISTERS = {"RESET": 0xE0,
                 "CRTL_MEAS": 0xF4,
                 "CONFIG": 0xF5,
                 "TRIMMING_START": 0x88,
                 "DATA": 0xF7}
    RESET_WORD = 0xB6
    TRIMMING_LENGTH = 24

    def __init__(self, address=None, i2c=None,
                 sda=None, scl=None):
        """
        Creattes a bme280 temperature, pressure and (optionally)
        humidity using I2C.

        Parameters
        ----------
        busaddress : int (optional)
            THe bus addres were the I2C devices are found. This should
            be 0 for the raspberrypi rev. 1 and 1 for the other (at
            least until rev3. For non raspberrypi devices you must
            find the correct value. Default 1.
        address : int or None (optioanl)
            The I2C address of the device. If None the default one
            will be used. Default None.

        bus : smbus.SMBus or None
            If not None an open bus were the object can be found. If
            None a new bus will be opened. Default None

        """

        self._chip_id = None
        self._chip_version = None
        self._trimming = {}
        self._data = {"temperature": None,
                      "pressure": None,
                      "humidity": None}
        self._config = {"mode": Modes.FORCE,
                        "temperature_oversampling": Oversampling.x1,
                        "pressure_oversampling": Oversampling.x1}
        self._normal_config = {"time_standby": Standby.t500,
                               "filter": Filter.OFF}

        if address is None:
            self._address = self.DEFAULT_ADDRESS
        else:
            self._address = address

        if i2c is None:
            if sda is None or scl is None:
                raise ValueError("Must specify sda and scl pins")
            self._i2c = I2C(sda=Pin(sda), scl=Pin(scl))
        else:
            self._i2c = i2c

        self._read_chip_info()
        self._read_trimming()

    def _read_trimming(self):
        # Trimmings for temperature
        trimming_start = self.REGISTERS["TRIMMING_START"]
        trimmings = self.i2c.readfrom_mem(self.address,
                                          trimming_start,
                                          self.TRIMMING_LENGTH)
        # combine the trims
        first = [i for index, i in enumerate(trimmings) if not index%2]
        second = [i for index, i in enumerate(trimmings) if index%2]
        trims = []
        for first, second in zip(first, second):
            trims.append(self._combine_bytes(first, second))
        trims[4:] = [value if value < 32768 else value-65536 for value in trims[4:]]
        self._trimming["temperature"] = trims[:3]
        self._trimming["pressure"] = trims[3:]

    def _read_data(self):
        data = self.i2c.readfrom_mem(self.address,
                                     self.REGISTERS["DATA"],
                                     8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        self._data["temperature"] = self._refine_temperature(temp_raw)
        self._data["pressure"] = self._refine_pressure(pres_raw)
        self._data["humidity"] = self._refine_humidity(hum_raw)

    def _write_conf(self):
        temp_over = self._config["temperature_oversampling"]
        press_over = self._config["pressure_oversampling"]
        mode = self._config["mode"]
        value = (temp_over << 5) | (press_over << 2) | mode
        self.i2c.writeto_mem(self.address,
                             self.REGISTERS["CRTL_MEAS"],
                             chr(value))

    def _write_normal_conf(self):
        standby = self._normal_config["time_standby"]
        filter_mod = self._normal_config["filter"]
        value = (standby << 5 | filter_mod << 2 | 0)
        self.i2c.writeto_mem(self.address,
                             self.REGISTERS["CONFIG"],
                             chr(value))
    @staticmethod
    def _combine_bytes(first, second):
        return (second << 8) + first

    def _read_chip_info(self):
        (self._chip_id,
         self._chip_version) = self.i2c.readfrom_mem(self.address,
                                                     0xD0, 2)

    def _refine_humidity(self, humidity):
        return

    def _refine_temperature(self, temperature):
        """
        Temperature must be int 32
        """
        # Witchcraft from the datasheet (page 23)

        dig1, dig2, dig3 = self._trimming["temperature"]

        var1 = ((((temperature>>3)-(dig1<<1)))*(dig2)) >> 11
        var2 = (((((temperature>>4) - (dig1))
                  * ((temperature>>4) - (dig1))) >> 12) * (dig3)) >> 14
        temperature_fine = var1 + var2
        return temperature_fine

    def _refine_pressure(self, pressure):
        # More witchcraft from page 23 of the datasheet

        (dig1, dig2, dig3, dig4, dig5, dig6,
         dig7, dig8, dig9) = self._trimming["pressure"]
        temperature = self._data["temperature"]

        var1 = (temperature/2.0) - 64000.0
        var2 = var1 * var1 * dig6 / 32768.0
        var2 = var2 + var1 * dig5 * 2.0
        var2 = (var2/4.0)+(dig4 * 65536.0)
        var1 = (dig3 * var1 * var1 / 524288.0 + dig2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig1
        if var1 == 0.0:
            return 0

        p_refined = 1048576.0 - pressure
        p_refined = (p_refined - (var2 / 4096.0)) * 6250.0 / var1
        var1 = dig9 * p_refined * p_refined / 2147483648.0
        var2 = p_refined * dig8 / 32768.0
        p_refined = p_refined + (var1 + var2 + dig7) / 16.0
        return p_refined

    @property
    def address(self):
        """
        I2C address of the sensor
        """
        return self._address
    @address.setter
    def address(self, value):
        self._address = value

    @property
    def i2c(self):
        """
        Returns the opened bus to the device
        """
        return self._i2c

    @property
    def chip_id(self):
        """
        Id of the chip
        """
        return self._chip_id

    @property
    def chip_version(self):
        """
        The version of the chip
        """
        return self._chip_version

    @property
    def temperature(self):
        """
        Returns the refined temperature
        """
        return float(((self._data["temperature"] * 5) +128) >> 8)/100.

    @property
    def pressure(self):
        """
        Returns the refined pressure
        """
        return self._data["pressure"] / 100.0

    @property
    def data(self):
        """
        Just extracted data. This method should be used when operating
        in normal mode
        """
        self._read_data()
        return self.temperature, self.pressure

    @property
    def status(self):
        """
        Returns the oversampling in temperature, pressure and current mode
        """
        value = self.i2c.readfrom_mem(self.address,
                                      self.REGISTERS["CTRL_MEAS"], 1)[0]

        temp_over = value >> 5
        value -= temp_over << 5

        hum_over = value >> 2
        value -= hum_over << 2

        return (temp_over, hum_over, value)

    @property
    def mode(self):
        """
        The execution mode
        """
        return self._config["mode"]
    @mode.setter
    def mode(self, value):
        self._config["mode"] = value
        self._write_conf()

    @property
    def temp_over(self):
        """
        THe temperature oversampling ( 3 bits)
        """
        return self._config["temperature_oversampling"]

    @temp_over.setter
    def temp_over(self, value):
        self._config["temperature_oversampling"] = value
        self._write_conf()

    @property
    def press_over(self):
        """
        The pressure oversmapling
        """
        return self._config["pressure_oversampling"]

    @press_over.setter
    def press_over(self, value):
        self._config["pressure_oversampling"] = value
        self._write_conf()

    @property
    def standby(self):
        """
        Standby time (encoded in 3 bytes, see Standby object)
        """
        return self._normal_config["time_standby"]

    @standby.setter
    def standby(self, value):
        self._normal_config["time_standby"] = value
        self._write_normal_conf()

    @property
    def filter_param(self):
        """
        The filter paramiter, see Filter object for the encoding
        """
        return self._normal_config["filter"]

    @filter_param.setter
    def filter_param(self, value):
        self._normal_config["filter"] = value
        self._write_normal_conf()

    def reset(self):
        """
        Resets the sensor
        """
        self.i2c.writeto_mem(self.address, self.REGISTERS["RESET"],
                             chr(self.RESET_WORD))

    def update(self):
        """
        Updates the readings of the sensor
        """
        self._write_conf()
        time.sleep(0.1)
        self._read_data()

class Modes(object):
    """
    Different modes for the bme280
    """
    SLEEP = 0
    FORCE = 1
    NORMAL = 3

class Oversampling(object):
    """
    Different Oversampling
    """
    SKIP = 0
    x1 = 1
    x2 = 2
    x4 = 3
    x8 = 4
    x16 = 5

class Standby(object):
    """
    Values for the different standby time(ms). THe _ reqresents the
    decimal point
    """
    t0_5 = 0
    t62_5 = 1
    t125 = 2
    t250 = 3
    t500 = 4
    t1000 = 5
    t10 = 6
    t20 = 7

class Filter(object):
    """
    Filters for the data
    """
    OFF = 0
    x2 = 1
    x4 = 2
    x8 = 3
    x16 = 4
