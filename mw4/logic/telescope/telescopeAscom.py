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
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class TelescopeAscom(AscomClass):
    """
    """

    __all__ = ['TelescopeAscom']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()

        value = self.getAscomProperty('ApertureDiameter')
        if isinstance(value, float):
            value = value * 1000

        self.storePropertyToData(value, 'TELESCOPE_INFO.TELESCOPE_APERTURE')

        value = self.getAscomProperty('FocalLength')
        if isinstance(value, float):
            value = value * 1000

        self.storePropertyToData(value, 'TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH')
        return True
