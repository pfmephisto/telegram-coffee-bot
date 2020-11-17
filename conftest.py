"""This is the set up for the testing environment"""

import sys
import platform

# If this is not a Raspberry Pi
if platform.machine() != 'armv7l':

    import fake_rpi
    from fake_rpi import toggle_print

    sys.modules['RPi'] = fake_rpi.RPi            # Fake RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO  # Fake GPIO
    sys.modules['smbus'] = fake_rpi.smbus        # Fake smbus (I2C)
    toggle_print(False)
