"""Test the coffee machine class"""

import sys
import datetime
import fake_rpi
from fake_rpi import toggle_print
from coffee_bot.coffee_machine import CoffeeMachine

sys.modules['RPi'] = fake_rpi.RPi            # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO  # Fake GPIO
sys.modules['smbus'] = fake_rpi.smbus        # Fake smbus (I2C)
toggle_print(False)


# Settings for testing
class TestSettings():
    """Class representing the settings used for testing"""
    BREWING = 14
    HEATING = 15
    timestamp = None
    NAME = 'TestMachine'


settings = TestSettings()

cm = CoffeeMachine(settings.NAME, settings.BREWING, settings.HEATING)


def test_last_coffee_none():
    """Test if the the coffee machine returns
    the last coffee state of None if furst turned on"""
    assert cm.last_coffee is None


def test_none():
    """Test if the the coffee machine returns the propper
        none state if first turned on"""
    fake_rpi.RPi.GPIO.set_input(settings.BREWING, 0)
    fake_rpi.RPi.GPIO.set_input(settings.HEATING, 0)
    assert cm.check_state() is None


def test_brewing():
    """Test if the the coffee machine returns the propper beewing state"""
    fake_rpi.RPi.GPIO.set_input(settings.BREWING, 1)
    fake_rpi.RPi.GPIO.set_input(settings.HEATING, 1)
    assert cm.State.BREWING == cm.check_state()


def test_ready():
    """Test if the the coffee machine returns the propper ready state"""
    fake_rpi.RPi.GPIO.set_input(settings.BREWING, 0)
    fake_rpi.RPi.GPIO.set_input(settings.HEATING, 1)
    settings.timestamp = datetime.datetime.now()
    assert cm.State.READY == cm.check_state()


def test_error():
    """test the coffee machine error state"""
    fake_rpi.RPi.GPIO.set_input(settings.BREWING, 1)
    fake_rpi.RPi.GPIO.set_input(settings.HEATING, 0)
    assert cm.State.ERROR == cm.check_state()


def test_off():
    """Test the off state of the coffee machine"""
    fake_rpi.RPi.GPIO.set_input(settings.BREWING, 0)
    fake_rpi.RPi.GPIO.set_input(settings.HEATING, 0)
    assert cm.State.OFF == cm.check_state()


def test_str():
    """Test the coffee machine string name"""
    assert str(cm) == settings.NAME


def test_int():
    """Test the coffee machine interger state"""
    cm.state = cm.State(1)
    assert int(cm) == 1


def test_last_coffee_time():
    """Test that the last coffee time has been propperly updated"""
    assert cm.last_coffee is not None and \
        cm.last_coffee.replace(microsecond=0) == \
        settings.timestamp.replace(microsecond=0)
