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
import logging
import platform

# external packages
import PyQt5

# local imports
from logic.dome.domeIndi import DomeIndi
from logic.dome.domeAlpaca import DomeAlpaca
if platform.system() == 'Windows':
    from logic.dome.domeAscom import DomeAscom


class DomeSignals(PyQt5.QtCore.QObject):
    """
    The DomeSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['DomeSignals']

    azimuth = PyQt5.QtCore.pyqtSignal(object)
    slewFinished = PyQt5.QtCore.pyqtSignal()
    message = PyQt5.QtCore.pyqtSignal(object)

    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal(object)
    deviceConnected = PyQt5.QtCore.pyqtSignal(str)
    deviceDisconnected = PyQt5.QtCore.pyqtSignal(str)


class Dome:

    __all__ = ['Dome',
               ]

    log = logging.getLogger(__name__)

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = DomeSignals()

        self.data = {
            'Slewing': False,
            'AzimuthTarget': 0,
        }
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': DomeIndi(self.app, self.signals, self.data),
            'alpaca': DomeAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == 'Windows':
            self.run['ascom'] = DomeAscom(self.app, self.signals, self.data)
            ascomSignals = self.run['ascom'].ascomSignals
            ascomSignals.serverConnected.connect(self.signals.serverConnected)
            ascomSignals.serverDisconnected.connect(self.signals.serverDisconnected)
            ascomSignals.deviceConnected.connect(self.signals.deviceConnected)
            ascomSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

        # signalling from subclasses to main
        alpacaSignals = self.run['alpaca'].client.signals
        alpacaSignals.serverConnected.connect(self.signals.serverConnected)
        alpacaSignals.serverDisconnected.connect(self.signals.serverDisconnected)
        alpacaSignals.deviceConnected.connect(self.signals.deviceConnected)
        alpacaSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        indiSignals = self.run['indi'].client.signals
        indiSignals.serverConnected.connect(self.signals.serverConnected)
        indiSignals.serverDisconnected.connect(self.signals.serverDisconnected)
        indiSignals.deviceConnected.connect(self.signals.deviceConnected)
        indiSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        self.app.update1s.connect(self.checkSlewingDome)
        self.useGeometry = False
        self.settlingTime = 0
        self.settlingWait = PyQt5.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitSettlingAndEmit)

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].startCommunication(loadConfig=loadConfig)
        return suc

    def stopCommunication(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        self.signals.message.emit('')
        suc = self.run[self.framework].stopCommunication()
        return suc

    def waitSettlingAndEmit(self):
        """
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

    def checkSlewingDome(self):
        """
        :return:
        """
        azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION', 0)
        hasToMove = self.diffModulus(azimuth, self.data['AzimuthTarget'], 360) > 1
        isSlewing = self.data['Slewing'] and hasToMove

        if isSlewing:
            self.signals.message.emit('slewing')

        if self.data['Slewing'] and not isSlewing:
            self.signals.message.emit('wait settle')
            self.settlingWait.start(self.settlingTime * 1000)

        self.data['Slewing'] = isSlewing
        self.signals.azimuth.emit(azimuth)

        return True

    def slewDome(self, altitude=0, azimuth=0):
        """

        :param altitude:
        :param azimuth:
        :return: success
        """

        if not self.data:
            return False

        mount = self.app.mount

        if self.useGeometry:
            alt, az, _, _, _ = mount.calcTransformationMatrices()

            if alt is None or az is None:
                self.log.info(f'Geometry error, alt:{altitude}, az:{azimuth}')
                alt = altitude
                az = azimuth

            else:
                alt = alt.degrees
                az = az.degrees

        else:
            alt = altitude
            az = azimuth

        delta = azimuth - az

        self.data['Slewing'] = True
        self.data['AzimuthTarget'] = azimuth
        self.run[self.framework].slewToAltAz(azimuth=az, altitude=alt)

        return delta
