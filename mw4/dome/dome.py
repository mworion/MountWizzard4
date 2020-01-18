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
# external packages
import PyQt5
import numpy as np
# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.dome.domeIndi import DomeIndi
from mw4.dome.domeAlpaca import DomeAlpaca


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
        self.framework = None
        self.run = {
            'indi': DomeIndi(self.app, self.signals, self.data),
            'alpaca': DomeAlpaca(self.app, self.signals, self.data),
        }
        self.name = ''

        self.host = ('localhost', 7624)
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

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        if self.framework in self.run.keys():
            self.run[self.framework].host = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        if self.framework in self.run.keys():
            self.run[self.framework].name = value

    @property
    def settlingTime(self):
        if self.framework in self.run.keys():
            return self.run[self.framework].settlingTime
        else:
            return None

    @settlingTime.setter
    def settlingTime(self, value):
        if self.framework in self.run.keys():
            self.run[self.framework].settlingTime = value

    def startCommunication(self):
        """

        """

        if self.framework in self.run.keys():
            suc = self.run[self.framework].startCommunication()
            return suc
        else:
            return False

    def stopCommunication(self):
        """

        """

        if self.framework in self.run.keys():
            self.signals.message.emit('')
            suc = self.run[self.framework].stopCommunication()
            return suc
        else:
            return False

    def slewDome(self, altitude=0, azimuth=0):
        """

        :param altitude:
        :param azimuth:
        :return: success
        """

        if not self.data:
            return False

        if self.isGeometry:
            ha = self.app.mount.obsSite.haJNowTarget.radians
            dec = self.app.mount.obsSite.decJNowTarget.radians
            lat = self.app.mount.obsSite.location.latitude.radians
            pierside = self.app.mount.obsSite.piersideTarget
            alt, az = self.app.mount.geometry.calcTransformationMatrices(ha=ha,
                                                                         dec=dec,
                                                                         lat=lat,
                                                                         pierside=pierside)
            alt = alt.degrees
            az = az.degrees

            # todo: correct calculation that this is not necessary
            if alt is np.nan or az is np.nan:
                self.log.warning(f'alt:{altitude}, az:{azimuth}, pier:{pierside}')

            if alt is np.nan:
                alt = altitude
            if az is np.nan:
                az = azimuth

        else:
            alt = altitude
            az = azimuth

        geoStat = 'Geometry corrected' if self.isGeometry else 'Equal mount'
        delta = azimuth - az
        text = f'Slewing  dome:       {geoStat}, az: {az:3.1f} delta: {delta:3.1f}°'
        self.app.message.emit(text, 0)

        suc = self.run[self.framework].slewToAltAz(azimuth=az, altitude=alt)

        return suc
