from . import BME280
import utime
from udevices.button import Button
from machine import Pin
from . import MultipleHistorial

class WeatherStation(object):
    """
    Simple weather station with screen
    """

    def __init__(self, sda, scl, update_time=60, pin_mode=15):
        from . import OLED
        self.oled = OLED()
        self.update_time = update_time

        self._screen_mode = 0
        self._change_button = Button(pin_mode, Pin.IN, Pin.PULL_UP)
        self._change_button.irq(self._change_mode, Pin.IRQ_FALLING)

        self.bme280 = BME280(sda=sda, scl=scl)
        self._historial = MultipleHistorial([2, 4])

        self.manual_update()

    def _change_mode(self, _):
        self._screen_mode = not self._screen_mode
        self._refresh_screen()

    def _read_values(self):
        # Read new values
        self.bme280.update()
        values = self.bme280.data
        self._historial.add(values)

    def _refresh_screen(self):
        if not self._screen_mode:
            self._setup_text()
        else:
            self._represent_values()

    def _setup_text(self):
        self.oled.fill(0)
        self.oled.text("Temp:      C", 16, 16)
        self.oled.text("Press:       hPa", 0, 40)
        # Print new values
        values = (self._historial[0][-1],
                  self._historial[1][-1])
        self._print_values(values, 1)
        self.oled.show()

    def manual_update(self):
        """
        Updates the values of temperature and pressure of the screen
        """
        self._read_values()
        self._refresh_screen()
        return

    def _print_values(self, values, color=1):
        self.oled.text("{:5.2f}".format(values[0]), 64, 16, color)
        self.oled.text("{:6.1f}".format(values[1]), 56, 40, color)

    def _represent_values(self):
        self._create_axis()
        self._create_labels()
        self._plot_data()
        self.oled.show()


    def _create_axis(self):
        self.oled.fill(0)
        # create the axis
        self.oled.line(41, 0,
                       41, 56, 1)
        self.oled.line(41, 56,
                       128, 56, 1)

        # Create some ticks
        for i in range(4):
            self.oled.line(41, 14*i,
                           43, 14*i, 1)

        for i in range(6):
            self.oled.line(46 + 16*i, 55,
                           46 + 16*i, 53, 1)

    def _create_labels(self, color=1):
        maximum = max(self._historial[0])
        minimum = min(self._historial[0])
        mean = (maximum + minimum) / 2

        self.oled.text("{:5.2f}".format(maximum),
                       0, 0, color)
        self.oled.text("{:5.2f}".format(mean),
                       0, 28, color)
        self.oled.text("{:5.2f}".format(minimum),
                       0, 56, color)
        # Scale of the y axis
        self.oled.text("x{:d}".format(4*self._historial.current), 80, 56)

    def _plot_data(self, color=1):
        maximum = max(self._historial[0])
        minimum = min(self._historial[0])

        last = None

        for i, temp in enumerate(self._historial[0]):
            yfraction = (temp - minimum) / (maximum - minimum)
            ycoord = int(56 * (1 - yfraction))
            xcoord = 46 + 4*i

            if last is None:
                last = (xcoord, ycoord)

            self.oled.line(xcoord, ycoord,
                           last[0], last[1],
                           color)
            last = (xcoord, ycoord)
        return


    def run_service(self):
        """
        Autoupdates with new values forever
        """
        print("starting")
        while True:
            self.manual_update()
            utime.sleep(self.update_time)
