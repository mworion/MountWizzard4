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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import warnings
import datetime
# external packages
# local imports


def setupLogging():
    """
    setupLogging defines the logger and formats and disables unnecessary library logging

    :return: true for test purpose
    """
    warnings.filterwarnings('ignore')
    name = 'mw4-{0}.log'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s]'
                               '[%(levelname)1.1s]'
                               # '[%(threadName)-.2s]'
                               '[%(filename)20s]'
                               '[%(lineno)4s]'
                               ' %(message)s',
                        handlers=[logging.FileHandler(name)],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )

    # setting different log level for imported packages to avoid unnecessary data
    logging.getLogger('mountcontrol').setLevel(logging.DEBUG)
    logging.getLogger('indibase').setLevel(logging.WARNING)
    logging.getLogger('PyQt5').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)
    # urllib3 is used by requests, so we have to add this as well
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)
    logging.getLogger('astropy').setLevel(logging.ERROR)
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
        print('log adapter:', msg)

        return f'{msg}', kwargs


