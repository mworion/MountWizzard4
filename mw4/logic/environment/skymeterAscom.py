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

# external packages

# local imports
from base.ascomClass import AscomClass


class SkymeterAscom(AscomClass):
    """
    the class SkymeterAscom inherits all information and handling of the Dome device.
    there will be some parameters who will define the slewing position of the dome relating
    to the
    """

    __all__ = ['SkymeterAscom',
               ]

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        self.getAndStoreAscomProperty('temperature', 'SKY_QUALITY.SKY_TEMPERATURE')
        self.getAndStoreAscomProperty('skyquality', 'SKY_QUALITY.SKY_BRIGHTNESS')
        return True
