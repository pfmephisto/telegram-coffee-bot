"""This class angles the generation of a password"""

import random

PASSWORD = ""


class Password():
    """This class angles the generation of a password"""
    def __init__(self):
        val = random.randrange(1000, 9999)
        self._val = int(val)

    def change(self):
        """Change the password"""
        val = random.randrange(1000, 9999)
        self._val = int(val)

    def __str__(self):
        return str(self._val)
