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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class FocuserAscom(AscomClass):
    """
    """

    __all__ = ['FocuserAscom']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        self.getAndStoreAscomProperty('Position',
                                      'ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION')
        return True

    def move(self, position=None):
        """
        :param position:
        :return:
        """
        if not self.deviceConnected:
            return False

        self.client.move(position)
        return True

    def halt(self):
        """
        :return:
        """
        if not self.deviceConnected:
            return False

        self.getAscomProperty('halt')
        return True
