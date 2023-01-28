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
from base.indiClass import IndiClass


class FocuserIndi(IndiClass):
    """
    the class FocuserIndi inherits all information and handling of the Focuser device

        >>> f = FocuserIndi(app=None)
    """

    __all__ = ['FocuserIndi',
               ]

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data)

    def move(self, position=None):
        """
        :param position:
        :return:
        """
        if self.device is None:
            return False

        pos = self.device.getNumber('ABS_FOCUS_POSITION')
        pos['FOCUS_ABSOLUTE_POSITION'] = position
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='ABS_FOCUS_POSITION',
                                        elements=pos,
                                        )
        return suc

    def halt(self):
        """
        :return:
        """
        if self.device is None:
            return False

        pos = self.device.getNumber('ABS_FOCUS_POSITION')
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='ABS_FOCUS_POSITION',
                                        elements=pos,
                                        )
        return suc
