"""Set up the arguments to be passed to the coffee bot"""

import argparse
from argparse import ArgumentParser
import logging


# Add ArgumentParser
def str2bool(value):
    """Convert a string to a boolean"""
    if isinstance(value, bool):
        return value
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def loglevel(value):
    """Set the logging level based on a string"""
    if isinstance(value, int):
        return value
    if value == "DEBUG":
        return logging.DEBUG
    if value == "INFO":
        return logging.INFO
    if value == "WARNING":
        return logging.WARNING
    if value == "ERROR":
        return logging.ERROR
    if value == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.INFO


parser = ArgumentParser(
    description='This bot will tell you if fresh coffee is ready')
parser.add_argument("-e",
                    dest='eraseDB',
                    default=False,
                    type=str2bool,
                    nargs='?',
                    # action='store_true',
                    help="erase data base file, start fresh",
                    metavar="bool")
parser.add_argument("-q",
                    dest='quiet',
                    default=False,
                    action='store_true',
                    # nargs='?', type=bool
                    help="This will supress all logging")
parser.add_argument("-l",
                    dest='level',
                    default=20,
                    type=loglevel,
                    help="The log level to be used.")
parser.add_argument("-t",
                    dest='mode',
                    default=False,
                    action='store_true',
                    help="This will make the bot run in test mode.")
args = parser.parse_args()

if __name__ == '__main__':
    pass
