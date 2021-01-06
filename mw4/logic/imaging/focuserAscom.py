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
    the class focuser inherits all information and handling of the focuser device.
    """

    __all__ = ['FocuserAscom',
               ]

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().getInitialConfig()
        if not self.deviceConnected:
            return False

        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.dataEntry(self.client.Position, 'ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION')
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

        self.client.halt
        return True
