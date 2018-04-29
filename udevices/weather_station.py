from . import BME280
import utime

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
        self._historial = (Deque(), Deque())

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
        self._historial[0].append(self._prev_values[0])
        self._historial[1].append(self._prev_values[1])
        # Print new values
        self._print_values(self._prev_values, 1)
        self.oled.show()
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
            self.oled.line(41,14*i,
                           43,14*i, 1)

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
        self.oled.text("x4", 80, 56)

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

        while True:
            self.manual_update()
            if len(self._historial[0]) > 3:
                self._represent_values()

            utime.sleep(self.update_time)


class Deque(list):
    def __init__(self, *args, max_len=20, **kwargs):
        self._max_len = max_len
        super(Deque, self).__init__(*args, **kwargs)
        self._check_size()

    def append(self, *args, **kwargs):
        super(Deque, self).append(*args, **kwargs)
        self._check_size()

    def _check_size(self):
        while len(self) > self._max_len:
            self.pop(0)


