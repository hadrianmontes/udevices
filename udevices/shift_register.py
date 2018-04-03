#!/usr/bin/env python3
"""
Implements shift register
"""
import time
from machine import Pin

class ShiftRegister(object):
    """
    Impletens an N bit shift register
    """
    DELAY = 0.0001

    def __init__(self, datapin, clockpin, shiftpin, nbits=8):
        self._datapin = Pin(datapin, Pin.OUT)
        self._clockpin = Pin(clockpin, Pin.OUT)
        self._shiftpin = Pin(shiftpin, Pin.OUT)
        self._nbits = nbits

    def set_byte(self, value, reset=True):
        """
        Sets the value of the output

        Parameters
        ----------
        value : int
            Value to which the register will be set
        reset : bool (optional)
            If true the previous register will be set to 0. If not the
            new register will be appended to the previous one. Default
            True.

        """

        bits = list('{0:0b}'.format(value))
        nbits = len(bits)
        if len(bits) > self.nbits:
            text = "Value {} exceeds maximum register value {}"
            text = text.format(value, 2**(self.nbits)-1)
            raise ValueError(text)
        self._shiftpin(0)
        time.sleep(self.DELAY)
        if reset:
            for _ in range(self.nbits - nbits):
                self._set_bit(0)
        for bit in bits:
            self._set_bit(int(bit))
        self._shiftpin(1)
        time.sleep(self.DELAY)
        self._shiftpin(0)

    def reset(self):
        """
        Resets the register to 0
        """
        self.set_byte(0)

    def _set_bit(self, state):
        self._datapin(state)
        time.sleep(self.DELAY)
        self._clockpin(1)
        time.sleep(self.DELAY)
        self._clockpin(0)

    @property
    def datapin(self):
        """
        The datapin
        """
        return self._datapin
    @property
    def clockpin(self):
        """
        The clock pin
        """
        return self._clockpin

    @property
    def shiftpin(self):
        """
        The shift pi
        """
        return self._shiftpin

    @property
    def nbits(self):
        """
        The number of bits of the register
        """
        return self._nbits
