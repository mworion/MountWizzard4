############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import logging
import time
from logging.handlers import RotatingFileHandler
import datetime
import sys

# external packages

# local imports


class LoggerWriter:
    # taken from:
    # https://stackoverflow.com/questions/19425736/
    # how-to-redirect-stdout-and-stderr-to-logger-in-python
    def __init__(self, level, mode, std):
        self.level = level
        self.mode = mode
        self.standard = std

    def write(self, message):
        first = True
        for line in message.rstrip().splitlines():
            if first:
                self.level(f'[{self.mode}] ' + line.strip())
                first = False
            else:
                self.level(' ' * 9 + line.strip())

    def flush(self):
        pass


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`.

    `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`).

    If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    This method was inspired by the answers to Stack Overflow post
    http://stackoverflow.com/q/2183233/2988730, especially
    http://stackoverflow.com/a/13638084/2988730

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()
    if hasattr(logging, levelName):
        return
    if hasattr(logging, methodName):
        return
    if hasattr(logging.getLoggerClass(), methodName):
        return

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)


def redirectSTD():
    """
    :return:
    """
    # transfer all sys outputs to logging
    sys.stderr = LoggerWriter(logging.getLogger().error, 'STDERR', sys.stderr)
    sys.stdout = LoggerWriter(logging.getLogger().info, 'STDOUT', sys.stdout)
    return True


def setupLogging(redirect=True):
    """
    setupLogging defines the logger and formats and disables unnecessary
    library logging

    :return: true for test purpose
    """
    if not os.path.isdir('./log'):
        os.mkdir('./log')

    logging.Formatter.converter = time.gmtime
    timeTag = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    logFile = f'./log/mw4-{timeTag}.log'
    logHandler = RotatingFileHandler(logFile, mode='a', maxBytes=100 * 1024 * 1024,
                                     backupCount=100, encoding=None, delay=False)
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s.%(msecs)03d]'
                               '[%(levelname)1.1s]'
                               '[%(filename)15.15s]'
                               '[%(lineno)4s]'
                               ' %(message)s',
                        handlers=[logHandler],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )

    # setting different log level for imported packages to avoid unnecessary data
    # urllib3 is used by requests, so we have to add this as well
    logging.getLogger('PyQt5').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('astropy').setLevel(logging.WARNING)
    logging.getLogger('keyring').setLevel(logging.WARNING)
    addLoggingLevel('HEADER', 55)
    addLoggingLevel('UI', 35)
    addLoggingLevel('TRACE', 5)
    if redirect:
        redirectSTD()
    return True


def setCustomLoggingLevel(level='WARN'):
    """
    :return: true for test purpose
    """
    logging.getLogger().setLevel(level)
    return True
