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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import warnings
import datetime
from dateutil.tz import tzutc

# external packages

# local imports


def setupLogging():
    """
    setupLogging defines the logger and formats and disables unnecessary library logging

    :return: true for test purpose
    """
    def timeTz(*args):
        return datetime.datetime.now(tzutc()).timetuple()

    logging.Formatter.converter = timeTz

    warnings.filterwarnings('ignore')
    name = 'mw4-{0}.log'.format(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s]'
                               '[%(levelname)1.1s]'
                               # '[%(threadName)-.2s]'
                               # '[%(funcName)4.4s]'
                               '[%(filename)15.15s]'
                               '[%(lineno)4s]'
                               ' %(message)s',
                        handlers=[logging.FileHandler(name)],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )
    #
    # setting different log level for the internal libraries we shift one step up
    # standard ERROR    will be CRITICAL    logging hard error statements without solution
    # standard WARNING  will be ERROR       classical warnings which still enables work
    # standard INFO     will be WARNING     all GUI interaction stuff with user
    # standard DEBUG    will be INFO        all functional interface parameters
    # missing TRACE     will be debug       all low level communications (IP, SPI, etc)
    #
    logging.getLogger('mountcontrol').setLevel(logging.INFO)
    logging.getLogger('indibase').setLevel(logging.INFO)

    # setting different log level for imported packages to avoid unnecessary data
    # urllib3 is used by requests, so we have to add this as well
    logging.getLogger('PyQt5').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)
    logging.getLogger('astropy').setLevel(logging.ERROR)
    return True


def setCustomLoggingLevel(level='WARN'):
    """
    Setting the log level according to the setting in the gui.

    :return: true for test purpose
    """

    logging.getLogger().setLevel(level)
    logging.getLogger('indibase').setLevel(level)
    logging.getLogger('mountcontrol').setLevel(level)

    return True


class CustomLogger(logging.LoggerAdapter):
    """
    The MWLog class offers an adapter interface interface to allow a more customized
    logging functionality.

    """

    __all__ = ['MWLog',
               'run']

    def process(self, msg, kwargs):
        """
        if you want to prepend or append the contextual information to the message string,
        you just need to subclass LoggerAdapter and override process() to do what you need.
        that's what i am doing here.

        :param msg:
        :param kwargs:
        :return:
        """

        return f'{msg}', kwargs
