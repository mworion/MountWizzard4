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

# external packages

# local imports
from mw4.base.loggerMW import CustomLogger


class DirectWeather:
    """
    the class DirectWeather inherits all information and handling of the environment device

        >>> DirectWeather(host=None,
        >>>         name=''
        >>>         )
    """

    __all__ = ['DirectWeather',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, app=None):

        self.app = app

        # minimum set for driver package built in
        self.framework = None
        self.run = {
            'built-in': self
        }
        self.name = ''
        self.data = {}

    @staticmethod
    def startCommunication(loadConfig=False):
        """
        startCommunication enables the cyclic polling in framework driver

        :param loadConfig:
        :return: success
        """

        return True

    @staticmethod
    def stopCommunication():

        return True
