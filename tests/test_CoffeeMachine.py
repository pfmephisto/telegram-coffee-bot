import sys
import datetime
import fake_rpi
from fake_rpi import toggle_print

sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO
sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)
toggle_print(False)

brewing = 14
heating = 15
timeStamp = None
Name = 'TestMachine'

import CoffeeMachine.coffeeMachine as CM
cm = CM.coffeeMachine(Name, brewing, heating)

def test_lastCoffee_None():
    assert None == cm.lastCoffee

def test_NONE():
    fake_rpi.RPi.GPIO.set_input(brewing, 0)
    fake_rpi.RPi.GPIO.set_input(heating, 0)
    assert None == cm.checkState()

def test_BREWING():
    fake_rpi.RPi.GPIO.set_input(brewing, 1)
    fake_rpi.RPi.GPIO.set_input(heating, 1)
    assert cm.State.BREWING == cm.checkState()

def test_READY():
    fake_rpi.RPi.GPIO.set_input(brewing, 0)
    fake_rpi.RPi.GPIO.set_input(heating, 1)
    global timeStamp
    timeStamp = datetime.datetime.now()
    assert cm.State.READY == cm.checkState()

def test_ERROR():
    fake_rpi.RPi.GPIO.set_input(brewing, 1)
    fake_rpi.RPi.GPIO.set_input(heating, 0)
    assert cm.State.ERROR == cm.checkState()

def test_OFF():
    fake_rpi.RPi.GPIO.set_input(brewing, 0)
    fake_rpi.RPi.GPIO.set_input(heating, 0)
    assert cm.State.OFF == cm.checkState() 

def test_str():
    assert str(cm) == Name

def test_int():
    cm.state = cm.State(1)
    assert int(cm) == 1

def test_lastCoffee_Time():
    global timeStamp
    lastCoffeeSimple = cm.lastCoffee

    timeStamp.replace(microsecond=0)
    lastCoffeeSimple.replace(microsecond=0)

    assert cm.lastCoffee is not None and lastCoffeeSimple == timeStamp


