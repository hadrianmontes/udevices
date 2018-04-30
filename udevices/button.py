from machine import Pin
import utime

class Button(Pin):
    """
    A software debounced button to use with triggers
    """

    def __init__(self, *args, debounce_time=0.1, **kwargs):
        self._debounce_time = debounce_time
        self._last_action = utime.time()
        self._irq_function = lambda _: None
        super(Button, self).__init__(*args, **kwargs)


    def _callback(self, _):
        current = utime.time()
        if (current - self._last_action) > self._debounce_time:
            self._last_action = current
            self._irq_function(_)

    def irq(self, handler=None, trigger=(Pin.IRQ_FALLING | Pin.IRQ_RISING),
            **kwargs):
        if handler is not None:
            self._irq_function = handler
            handler = self._callback
        super(Button, self).irq(handler, trigger, **kwargs)
