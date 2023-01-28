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

# external packages

# local imports
from base.alpacaClass import AlpacaClass


class SkymeterAlpaca(AlpacaClass):
    """
    """

    __all__ = ['SkymeterAlpaca']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)

        self.signals = signals
        self.data = data

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.getAndStoreAlpacaProperty('temperature',
                                       'SKY_QUALITY.SKY_TEMPERATURE')
        self.getAndStoreAlpacaProperty('skyquality',
                                       'SKY_QUALITY.SKY_BRIGHTNESS')
        return True
