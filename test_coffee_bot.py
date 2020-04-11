import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')


import fake_rpi
from fake_rpi import toggle_print
sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO
sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)
toggle_print(False)

import coffee_bot
import jokes

#def test_news():
#    assert type(jokes.randomJoke()) == type(dict())

#def input(self, a):
#    return 1
#funcType = type(GPIO.input)
#GPIO.input = funcType(input, GPIO)
