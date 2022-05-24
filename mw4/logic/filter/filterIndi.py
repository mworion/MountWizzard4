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
from base.indiClass import IndiClass


class FilterIndi(IndiClass):
    """
    the class FilterIndi inherits all information and handling of the FilterWheel device

        >>> f = FilterIndi(app=None)
    """

    __all__ = ['FilterIndi',
               ]

    UPDATE_RATE = 1

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data)

    def sendFilterNumber(self, filterNumber=1):
        """
        :param filterNumber:
        :return: success
        """
        if self.device is None:
            return False

        filterNo = self.device.getNumber('FILTER_SLOT')
        filterNo['FILTER_SLOT_VALUE'] = filterNumber
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='FILTER_SLOT',
                                        elements=filterNo,
                                        )
        return suc
