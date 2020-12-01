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
# written in python3, (c) 2019, 2020 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class CoverAscom(AscomClass):
    """
    the class Dome inherits all information and handling of the Dome device. there will be
    some parameters who will define the slewing position of the dome relating to the
    mount.dome = DomeAscom(app=None)
    """

    __all__ = ['CoverAscom',
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

        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        states = ['NotPresent', 'Closed', 'Moving', 'Open', 'Unknown', 'Error']

        if not self.deviceConnected:
            return False

        state = self.client.coverstate
        stateText = states[state]
        self.dataEntry(stateText, 'Status.Cover')

        return True

    def sendCoverPark(self, park=True):
        """
        :return: true for test purpose
        """

        if not self.deviceConnected:
            return False

        if park:
            self.client.closecover

        else:
            self.client.opencover

        return True
