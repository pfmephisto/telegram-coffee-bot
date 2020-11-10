from enum import Enum

import RPi.GPIO as GPIO   # Import Raspberry Pi GPIO library
import datetime

GPIO.setwarnings(False)   # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering


class coffeeMachine:

    class State(Enum):
        OFF = 0
        BREWING = 1
        READY = 2
        ERROR = 3

    def __init__(self, name, Brewing_Signal=14, Heating_Signal=15):
        self.name = str(name)
        self.state = self.State.OFF
        self.lastCoffee = None

        # Set pins to be an input pin and
        # set initial value to be pulled low (off)
        self.brewingSig = Brewing_Signal
        self.heatingSig = Heating_Signal

        GPIO.setup(self.brewingSig, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.heatingSig, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def __str__(self):
        return self.name

    def __int__(self):
        return int(self.state.value)

    def chst(self, val):
        self.state = val
        if(val == self.State.READY):
            self.lastCoffee = datetime.datetime.now()

    def strState(self):
        text = {
            self.State.OFF: 'I hope your are ready to survive the ice age',
            self.State.BREWING: 'Set a timer, coffee will be ready soon',
            self.State.READY: 'Get it while it\'s hot',
            self.State.ERROR: 'Oh no something has gone wrong'
        }
        return text[self.state]

    def resetSingals(self):
        self.brewing_MS = \
            self.coffeReady_MS = \
            self.off_MS = \
            self.error_MS = False

    def checkState(self):

        brewing = GPIO.input(self.brewingSig)
        heating = GPIO.input(self.heatingSig)

        if (brewing == GPIO.HIGH and
            heating == GPIO.HIGH and not
                self.state == self.State.BREWING):
            self.chst(self.State.BREWING)
            return self.State.BREWING
        if (brewing != GPIO.HIGH and
            heating == GPIO.HIGH and not
                self.state == self.State.READY):
            self.chst(self.State.READY)
            return self.State.READY
        if (brewing != GPIO.HIGH and
            heating != GPIO.HIGH and not
                self.state == self.State.OFF):
            self.chst(self.State.OFF)
            return self.State.OFF
        if (brewing == GPIO.HIGH and
            heating != GPIO.HIGH and not
                self.state == self.State.ERROR):
            self.chst(self.State.ERROR)
            return self.State.ERROR
