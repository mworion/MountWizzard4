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
import logging
# external packages
import PyQt5
# local imports
from base.loggerMW import CustomLogger
from base.indiClass import IndiClass


class DomeIndi(IndiClass):
    """
    the class Dome inherits all information and handling of the Dome device. there will be
    some parameters who will define the slewing position of the dome relating to the mount.

        >>> dome = DomeIndi(app=None)
    """

    __all__ = ['DomeIndi',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data
        self.settlingTime = 0
        self.azimuthTarget = 0
        self.slewing = False

        self.app.update1s.connect(self.updateStatus)

        self.settlingWait = PyQt5.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitSettlingAndEmit)

    @property
    def settlingTime(self):
        return self._settlingTime * 1000

    @settlingTime.setter
    def settlingTime(self, value):
        self._settlingTime = value

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of dome devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """

        if deviceName != self.deviceName:
            return False

        if self.device is None:
            return False

        update = self.device.getNumber('POLLING_PERIOD')

        if 'PERIOD_MS' not in update:
            return False

        if update.get('PERIOD_MS', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD_MS'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING_PERIOD',
                                        elements=update,
                                        )

        return suc

    def updateStatus(self):
        """
        updateStatus emits the actual azimuth status every 3 second in case of opening a
        window and get the signals late connected as INDI does nt repeat any signal of it's
        own

        :return: true for test purpose
        """

        if not self.client.connected:
            return False

        azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION', 0)
        self.signals.azimuth.emit(azimuth)

        return True

    def waitSettlingAndEmit(self):
        """
        waitSettlingAndEmit emit the signal for slew finished

        :return: true for test purpose
        """

        self.signals.slewFinished.emit()
        self.signals.message.emit('')

        return True

    @staticmethod
    def diffModulus(x, y, m):
        """
        :param x:
        :param y:
        :param m:
        :return:
        """
        diff = abs(x - y)
        diff = abs(diff % m)
        return min(diff, abs(diff - m))

    def updateNumber(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """
        if not super().updateNumber(deviceName, propertyName):
            return False

        for element, value in self.device.getNumber(propertyName).items():

            if element != 'DOME_ABSOLUTE_POSITION':
                continue

            azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION', 0)
            hasToMove = self.diffModulus(azimuth, self.azimuthTarget, 360) > 1
            isSlewing = self.slewing and hasToMove

            if isSlewing:
                self.signals.message.emit('slewing')

            else:
                self.signals.message.emit('')

            if self.slewing and not isSlewing:
                self.signals.message.emit('settle')
                self.settlingWait.start(self.settlingTime)

            self.slewing = isSlewing
            self.signals.azimuth.emit(azimuth)

        return True

    def slewToAltAz(self, altitude=0, azimuth=0):
        """
        slewToAltAz sends a command to the dome to move to azimuth / altitude. if a dome
        does support this

        :param altitude:
        :param azimuth:
        :return: success
        """

        if self.device is None:
            return False

        if self.deviceName is None or not self.deviceName:
            return False

        position = self.device.getNumber('ABS_DOME_POSITION')

        if 'DOME_ABSOLUTE_POSITION' not in position:
            return False

        position['DOME_ABSOLUTE_POSITION'] = azimuth

        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='ABS_DOME_POSITION',
                                        elements=position,
                                        )

        self.slewing = True
        self.azimuthTarget = azimuth
        self.signals.message.emit('slewing')

        return suc
