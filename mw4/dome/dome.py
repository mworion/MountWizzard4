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
import platform

# external packages
import PyQt5

# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.dome.domeIndi import DomeIndi
from mw4.dome.domeAlpaca import DomeAlpaca
if platform.system() == 'Windows':
    from mw4.dome.domeAscom import DomeAscom


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

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, app):

        self.app = app
        self.threadPool = app.threadPool
        self.signals = DomeSignals()

        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = None
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

        self.isGeometry = False

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

    def startCommunication(self, loadConfig=False):
        """

        """

        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].startCommunication(loadConfig=loadConfig)
        return suc

    def stopCommunication(self):
        """

        """

        if self.framework not in self.run.keys():
            return False

        self.signals.message.emit('')
        suc = self.run[self.framework].stopCommunication()
        return suc

    def slewDome(self, altitude=0, azimuth=0, piersideT='', haT=None, decT=None, lat=None):
        """

        :param altitude:
        :param azimuth:
        :param piersideT: target of pierside for slew
        :param haT: target hours angle for slew
        :param decT: target declination for slew
        :param lat: latitude of mount position
        :return: success
        """

        if not self.data:
            return False

        geometry = self.app.mount.geometry

        if piersideT:
            alt, az, _, _, _ = geometry.calcTransformationMatrices(ha=haT,
                                                                   dec=decT,
                                                                   lat=lat,
                                                                   pierside=piersideT)

            if alt is None or az is None:
                self.log.warning(f'Geometry E: {haT.radians}, {decT.radians}, {piersideT}')
                alt = altitude
                az = azimuth
            else:
                alt = alt.degrees
                az = az.degrees

        else:
            alt = altitude
            az = azimuth

        delta = azimuth - az
        self.run[self.framework].slewToAltAz(azimuth=az, altitude=alt)

        return delta
