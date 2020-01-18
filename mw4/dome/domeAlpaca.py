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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
from datetime import datetime
# external packages
import PyQt5
import numpy as np
# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.alpacaBase import Dome
from mw4.base.tpool import Worker


class DomeAlpaca(AlpacaClass):
    """
    the class Dome inherits all information and handling of the Dome device. there will be
    some parameters who will define the slewing position of the dome relating to the
    mount.dome = DomeAlpaca(app=None)
    """

    __all__ = ['DomeAlpaca',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = Dome()
        self.signals = signals
        self.data = data
        self.settlingTime = 0
        self.azimuth = 0
        self.slewing = False

        self.app.update1s.connect(self.startPollData)

        self.settlingWait = PyQt5.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitSettlingAndEmit)

    @property
    def settlingTime(self):
        return self._settlingTime * 1000

    @settlingTime.setter
    def settlingTime(self, value):
        self._settlingTime = value

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
        isSlewing = self.data.get('slewing', False)

        self.signals.azimuth.emit(azimuth)

        if isSlewing:
            self.signals.message.emit('slewing')
        else:
            self.signals.message.emit('')

        if self.slewing and not isSlewing:
            # start timer for settling time and emit signal afterwards
            self.settlingWait.start(self.settlingTime)

        self.slewing = isSlewing

        return True

    def pollData(self):
        """

        :return: true for test purpose
        """
        self.data['ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION'] = self.client.azimuth()
        self.data['slewing'] = self.client.slewing()
        return True

    def startPollData(self):
        """

        :return: success
        """

        if not self.deviceConnected:
            return False

        worker = Worker(self.pollData)
        worker.signals.result.connect(self.emitData)
        self.threadPool.start(worker)
        return True

    def slewToAltAz(self, altitude=0, azimuth=0):
        """
        slewToAltAz sends a command to the dome to move to azimuth / altitude. if a dome
        does support this

        :param altitude:
        :param azimuth:
        :return: success
        """

        self.client.slewtoazimuth(Azimuth=azimuth)
        self.slewing = True

        return True
