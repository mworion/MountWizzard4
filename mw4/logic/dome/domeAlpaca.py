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
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.alpacaBase import Dome


class DomeAlpaca(AlpacaClass):
    """
    the class Dome inherits all information and handling of the Dome device. there will be
    some parameters who will define the slewing position of the dome relating to the
    mount.dome = DomeAlpaca(app=None)
    """

    __all__ = ['DomeAlpaca',
               ]

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = Dome()
        self.signals = signals
        self.data = data
        self.settlingTime = 0
        self.azimuth = 0
        self.slewing = False
        self.targetAzimuth = -999
        self.targetAltitude = -999

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

    def emitData(self):
        """

        :return: true for test purpose
        """

        azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION', 0)
        statusIsSlewing = self.data.get('slewing', False)
        hasReachedTarget = (azimuth - self.targetAzimuth) < 0.1
        isSlewing = statusIsSlewing or not hasReachedTarget
        hasStopped = self.slewing and not statusIsSlewing and hasReachedTarget

        if isSlewing:
            self.slewing = True

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
        self.dataEntry(self.client.azimuth(), 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION')
        val = self.client.shutterstatus()
        if val == 0:
            val = True
        else:
            val = False
        self.dataEntry(val,
                       'DOME_SHUTTER.SHUTTER_OPEN',
                       elementInv='DOME_SHUTTER.SHUTTER_CLOSED')
        self.dataEntry(self.client.slewing(), 'slewing')
        return True

    def slewToAltAz(self, altitude=0, azimuth=0):
        """
        slewToAltAz sends a command to the dome to move to azimuth / altitude. if a dome
        does support this

        :param altitude:
        :param azimuth:
        :return: success
        """

        self.slewing = True
        self.targetAzimuth = azimuth
        self.targetAltitude = altitude
        self.client.slewtoazimuth(Azimuth=azimuth)

        return True
