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
from base.indiClass import IndiClass


class FocuserIndi(IndiClass):
    """
    the class FocuserIndi inherits all information and handling of the Focuser device

        >>> f = FocuserIndi(app=None)
    """

    __all__ = ['FocuserIndi',
               ]

    UPDATE_RATE = 1

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of weather devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """

        if deviceName != self.deviceName:
            return False

        if self.device is None:
            return False

        update = self.device.getNumber('PERIOD_MS')

        if 'PERIOD' not in update:
            return False

        if update.get('PERIOD', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='PERIOD_MS',
                                        elements=update)
        return suc

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
