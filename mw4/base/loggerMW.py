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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import datetime
from dateutil.tz import tzutc

# external packages

# local imports


def timeTz(*args):
    return datetime.datetime.now(tzutc()).timetuple()


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


def setupLogging():
    """
    setupLogging defines the logger and formats and disables unnecessary
    library logging

    :return: true for test purpose
    """
    logging.Formatter.converter = timeTz
    timeTag = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    name = f'mw4-{timeTag}.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s.%(msecs)03d]'
                               '[%(levelname)1.1s]'
                               '[%(filename)15.15s]'
                               '[%(lineno)4s]'
                               ' %(message)s',
                        handlers=[logging.FileHandler(name)],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )

    # setting different log level for imported packages to avoid unnecessary data
    # urllib3 is used by requests, so we have to add this as well
    logging.getLogger('PyQt5').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    # logging.getLogger('astropy').setLevel(logging.WARNING)
    addLoggingLevel('HEADER', 55)
    addLoggingLevel('UI', 35)
    addLoggingLevel('TRACE', 5)
    return True


def setCustomLoggingLevel(level='WARN'):
    """
    :return: true for test purpose
    """
    logging.getLogger().setLevel(level)
    return True
