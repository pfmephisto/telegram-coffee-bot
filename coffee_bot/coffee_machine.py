"""This is the coffee machine class"""

import sys
import platform
import datetime
from enum import Enum

# If this is not a Raspberry Pi
if platform.machine() != 'armv7l':

    import fake_rpi
    from fake_rpi import toggle_print

    sys.modules['RPi'] = fake_rpi.RPi            # Fake RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO  # Fake GPIO
    sys.modules['smbus'] = fake_rpi.smbus        # Fake smbus (I2C)
    toggle_print(False)
    fake_rpi.RPi.GPIO.set_input(15, 0)
    fake_rpi.RPi.GPIO.set_input(14, 0)
import RPi.GPIO as GPIO   # Import Raspberry Pi GPIO library


GPIO.setwarnings(False)   # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering


class CoffeeMachine:
    """Coffee machine class"""
    class State(Enum):
        """Enumerable class representing the different
        states of the coffee machine"""
        OFF = 0
        BREWING = 1
        READY = 2
        ERROR = 3

    def __init__(self, name, Brewing_Signal=14, Heating_Signal=15):
        self.name = str(name)
        self.state = self.State.OFF
        self.last_coffee = None

        # Set pins to be an input pin and
        # set initial value to be pulled low (off)
        self.brewing_sig = Brewing_Signal
        self.heating_sig = Heating_Signal

        GPIO.setup(self.brewing_sig, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.heating_sig, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def __str__(self):
        return self.name

    def __int__(self):
        return int(self.state.value)

    def chst(self, val):
        """Check state and in case it is reasy set the
        time for when the last coffee has been brewed"""
        self.state = val
        if val == self.State.READY:
            self.last_coffee = datetime.datetime.now()

    def str_state(self):
        """Get a string representation of the cofeee machine state"""
        text = {
            self.State.OFF: 'I hope your are ready to survive the ice age',
            self.State.BREWING: 'Set a timer, coffee will be ready soon',
            self.State.READY: 'Get it while it\'s hot',
            self.State.ERROR: 'Oh no something has gone wrong'
        }
        return text[self.state]

    def reset_singals(self):
        """Reset the coffee machine signal"""
        self.state = None

    def check_state(self):
        """Check the state the coffee machine is in"""
        brewing = GPIO.input(self.brewing_sig)
        heating = GPIO.input(self.heating_sig)

        if (brewing == GPIO.HIGH and
            heating == GPIO.HIGH and
                self.state != self.State.BREWING):
            self.chst(self.State.BREWING)
            return self.State.BREWING
        if (brewing != GPIO.HIGH and
            heating == GPIO.HIGH and
                self.state != self.State.READY):
            self.chst(self.State.READY)
            return self.State.READY
        if (brewing != GPIO.HIGH and
            heating != GPIO.HIGH and
                self.state != self.State.OFF):
            self.chst(self.State.OFF)
            return self.State.OFF
        if (brewing == GPIO.HIGH and
            heating != GPIO.HIGH and
                self.state != self.State.ERROR):
            self.chst(self.State.ERROR)
            return self.State.ERROR
