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
from datetime import datetime
# external packages
import numpy as np
# local imports
from mw4.base import indiClass


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

    def __init__(self, app=None):

        self.app = app

        # minimum set for driver package built in
        self.framework = None
        self.run = {
            'built-in': self
        }
        self.name = ''

    @staticmethod
    def startCommunication():
        return True

    @staticmethod
    def stopCommunication():
        return True
