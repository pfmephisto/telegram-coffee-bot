# Load enviroment variables
from dotenv import load_dotenv
if (not load_dotenv()):
    print('No Enviroment loaded')

import Jokes.jokes as jokes


def test_RANDOM():
    j1 = jokes.randomJoke()
    j2 = jokes.randomJoke()
    assert j1 != j2
