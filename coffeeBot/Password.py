import random


class password():
    def __init__(self):
        val = random.randrange(1000, 9999)
        self._val = int(val)

    def change(self):
        val = random.randrange(1000, 9999)
        self._val = int(val)

    def __str__(self):
        return str(self._val)
