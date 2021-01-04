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

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """

        super().getInitialConfig()

        return True

    def workerPollData(self):
        """

        :return: true for test purpose
        """

        if not self.deviceConnected:
            return False

        self.dataEntry(self.client.temperature, 'SKY_QUALITY.SKY_TEMPERATURE')
        self.dataEntry(self.client.skyquality, 'SKY_QUALITY.SKY_BRIGHTNESS')

        return True
