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
        self.isSlewing = False
        self.counterStartSlewing = -1
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

    def checkSlewingDome(self):
        """
        :return:
        """
        if self.isSlewing:
            self.signals.message.emit('slewing')
            self.counterStartSlewing = -1
            if not self.data.get('Slewing', True):
                self.isSlewing = False
                self.signals.message.emit('wait settle')
                self.settlingWait.start(self.settlingTime * 1000)

        else:
            if self.data.get('Slewing', True):
                self.log.debug('Slewing start by signal')
                self.isSlewing = True

            else:
                if self.counterStartSlewing == 0:
                    self.log.debug('Slewing start by counter')
                    self.isSlewing = True
                self.counterStartSlewing -= 1

        return True

    def slewDome(self, altitude=0, azimuth=0):
        """
        :param altitude:
        :param azimuth:
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
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

        self.signals.message.emit('slewing')
        self.counterStartSlewing = 3
        self.run[self.framework].slewToAltAz(azimuth=az, altitude=alt)
        delta = azimuth - az
        return delta

    def openShutter(self):
        """
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        suc = self.run[self.framework].openShutter()
        return suc

    def closeShutter(self):
        """
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        suc = self.run[self.framework].closeShutter()
        return suc

    def abortSlew(self):
        """
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        suc = self.run[self.framework].abortSlew()
        return suc
