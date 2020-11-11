import argparse
from argparse import ArgumentParser
import logging


# Add ArgumentParser
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def loglevel(v):
    if isinstance(v, int):
        return v
    if (v == "DEBUG"):
        return logging.DEBUG
    if (v == "INFO"):
        return logging.INFO
    if (v == "WARNING"):
        return logging.WARNING
    if (v == "ERROR"):
        return logging.ERROR
    if (v == "CRITICAL"):
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
