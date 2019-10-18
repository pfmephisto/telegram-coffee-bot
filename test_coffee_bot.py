#import sys, os
#myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')
from fake_rpi
sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi (GPIO)
sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)

import coffee_bot
import jokes

def test_news():
    assert type(jokes.randomJoke()) == type(dict())
