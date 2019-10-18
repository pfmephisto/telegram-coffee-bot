import coffee_bot
import jokes

def test_news():
    assert type(jokes.randomJoke()) == type(dict())
