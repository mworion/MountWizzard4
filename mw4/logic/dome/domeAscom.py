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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5

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

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.signals = signals
        self.data = data
        self.settlingTime = 0
        self.azimuth = 0
        self.slewing = False
        self.targetAzimuth = None
        self.targetAltitude = None

        self.settlingWait = PyQt5.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitSettlingAndEmit)

    @property
    def settlingTime(self):
        return self._settlingTime * 1000

    @settlingTime.setter
    def settlingTime(self, value):
        self._settlingTime = value

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """

        super().getInitialConfig()

        return True

    def waitSettlingAndEmit(self):
        """
        waitSettlingAndEmit emit the signal for slew finished

        :return: true for test purpose
        """

        self.signals.slewFinished.emit()

        return True

    @staticmethod
    def diffModulus(x, y, m):
        diff = abs(x - y)
        diff = abs(diff % m)
        return min(diff, abs(diff - m))

    def emitData(self):
        """

        :return: true for test purpose
        """

        azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION', -1)
        statusIsSlewing = self.data.get('slewing', False)

        if self.targetAzimuth is not None:
            hasReachedTarget = self.diffModulus(azimuth, self.targetAzimuth, 360) < 0.5

        else:
            hasReachedTarget = True

        hasStopped = self.slewing and (not statusIsSlewing or hasReachedTarget)

        if not self.slewing:
            self.slewing = statusIsSlewing and not hasReachedTarget

        if hasStopped:
            # start timer for settling time and emit signal afterwards
            self.settlingWait.start(self.settlingTime)
            self.slewing = False

        self.signals.azimuth.emit(azimuth)

        if self.slewing:
            self.signals.message.emit('slewing')

        else:
            self.signals.message.emit('')

        return True

    def workerPollData(self):
        """

        :return: true for test purpose
        """

        if not self.deviceConnected:
            return False

        self.dataEntry(self.client.Azimuth, 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION')
        self.dataEntry(self.client.Slewing, 'slewing')

        # unfortunately we cannot simply know, which properties are implemented, so we need to test
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

        self.slewing = True
        self.targetAzimuth = azimuth
        self.targetAltitude = altitude
        self.client.SlewToAzimuth(azimuth)

        return True
