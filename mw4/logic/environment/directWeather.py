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

# external packages

# local imports


class DirectWeather:
    """
    the class DirectWeather inherits all information and handling of the environment device

        >>> DirectWeather(host=None,
        >>>         name=''
        >>>         )
    """

    __all__ = ['DirectWeather',
               ]

    log = logging.getLogger(__name__)

    def __init__(self, app=None):

        self.app = app

        # minimum set for driver package built in
        self.framework = ''
        self.run = {
            'internal': self
        }
        self.deviceName = ''
        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {'internal': {'deviceName': 'Direct'}}}

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
