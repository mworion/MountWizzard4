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


class FocuserAlpaca(AlpacaClass):
    """
    the class focuser inherits all information and handling of the focuser device.
    """
    __all__ = ['FocuserAlpaca']

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

        self.getAndStoreAlpacaProperty('position',
                                       'ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION')
        return True

    def move(self, position=None):
        """
        :param position:
        :return:
        """
        if not self.deviceConnected:
            return False

        self.setAlpacaProperty('move', Position=position)
        return True

    def halt(self):
        """
        :return:
        """
        if not self.deviceConnected:
            return False

        self.getAlpacaProperty('halt')
        return True
