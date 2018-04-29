from . import BME280
import time

class WeatherStation(object):
    """
    Simple weather station with screen
    """

    def __init__(self, sda, scl, update_time=60):
        from . import OLED
        self.oled = OLED()
        self.update_time = update_time

        self.bme280 = BME280(sda=sda, scl=scl)
        self._prev_values = (0, 0)

        self._setup_text()
        self.manual_update()

    def _setup_text(self):
        self.oled.text("Temp:      C", 16, 16)
        self.oled.text("Press:       hPa", 0, 40)
        self.oled.show()

    def manual_update(self):
        """
        Updates the values of temperature and pressure of the screen
        """

        # clear previous values
        self._print_values(self._prev_values, 0)
        # Read new values
        self.bme280.update()
        self._prev_values = self.bme280.data
        # Print new values
        self._print_values(self._prev_values, 1)
        self.oled.show()
        return

    def _print_values(self, values, color=1):
        self.oled.text("{:5.2f}".format(values[0]), 64, 16, color)
        self.oled.text("{:6.1f}".format(values[1]), 56, 40, color)

    def run_service(self):
        """
        Autoupdates with new values forever
        """

        while True:
            self.manual_update()
            time.sleep(self.update_time)
