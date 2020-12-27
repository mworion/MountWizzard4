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
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class DomeAscom(AscomClass):
    """
    the class Dome inherits all information and handling of the Dome device. there will be
    some parameters who will define the slewing position of the dome relating to the
    mount.dome = DomeAscom(app=None)
    """

    __all__ = ['DomeAscom',
               ]

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def processPolledData(self):
        """
        :return: true for test purpose
        """
        azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION', 0)
        self.signals.azimuth.emit(azimuth)

        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.dataEntry(self.client.Azimuth,
                       'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION')
        print(self.data)

        # unfortunately we cannot simply know, which properties are implemented,
        # so we need to test
        try:
            val = self.client.shutterstatus

        except Exception:
            val = None

        else:
            if val == 0:
                val = True

            else:
                val = False

        if val is not None:
            self.dataEntry(val,
                           'DOME_SHUTTER.SHUTTER_OPEN',
                           elementInv='DOME_SHUTTER.SHUTTER_CLOSED')

        return True

    def slewToAltAz(self, altitude=0, azimuth=0):
        """
        slewToAltAz sends a command to the dome to move to azimuth / altitude. if a dome
        does support this

        :param altitude:
        :param azimuth:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.signals.message.emit('slewing')
        self.callMethodThreaded(self.client.SlewToAzimuth, azimuth)
        # self.client.SlewToAzimuth(azimuth)

        return True
