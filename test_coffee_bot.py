import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import coffee_bot
import jokes

def test_news():
    assert type(jokes.randomJoke()) == type(dict())
