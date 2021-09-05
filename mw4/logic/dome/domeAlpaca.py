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
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.alpacaClass import AlpacaClass
from base.alpacaBase import Dome


class DomeAlpaca(AlpacaClass):
    """
    the class Dome inherits all information and handling of the Dome device.
    there will be some parameters who will define the slewing position of the
    dome relating to the mount.dome = DomeAlpaca(app=None)
    """

    __all__ = ['DomeAlpaca',
               ]

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.client = Dome()
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

        shutterStates = ['Open', 'Closed', 'Opening', 'Closing', 'Error']

        azimuth = self.client.azimuth()
        self.storePropertyToData(azimuth, 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION')
        self.signals.azimuth.emit(azimuth)
        self.storePropertyToData(self.client.slewing(), 'Slewing')
        self.storePropertyToData(self.client.cansetaltitude(), 'CanSetAltitude')
        self.storePropertyToData(self.client.cansetazimuth(), 'CanSetAzimuth')
        self.storePropertyToData(self.client.cansetshutter(), 'CanSetShutter')

        state = self.client.shutterstatus()
        if state == 0:
            stateText = shutterStates[state]
            self.storePropertyToData(stateText, 'Status.Shutter')
            self.storePropertyToData(True,
                                     'DOME_SHUTTER.SHUTTER_OPEN',
                                     elementInv='DOME_SHUTTER.SHUTTER_CLOSED')
        elif state == 1:
            stateText = shutterStates[state]
            self.storePropertyToData(stateText, 'Status.Shutter')
            self.storePropertyToData(False,
                                     'DOME_SHUTTER.SHUTTER_OPEN',
                                     elementInv='DOME_SHUTTER.SHUTTER_CLOSED')
        else:
            self.data['DOME_SHUTTER.SHUTTER_OPEN'] = None
            self.data['DOME_SHUTTER.SHUTTER_CLOSED'] = None

        return True

    def slewToAltAz(self, altitude=0, azimuth=0):
        """
        slewToAltAz sends a command to the dome to move to azimuth / altitude.
        if a dome does support this

        :param altitude:
        :param azimuth:
        :return: success
        """
        if not self.deviceConnected:
            return False

        if self.data.get('CanSetAzimuth'):
            self.client.slewtoazimuth(Azimuth=azimuth)
        if self.data.get('CanSetAltitude'):
            self.client.slewtoaltitude(Altitude=altitude)
        return True

    def openShutter(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        if self.data.get('CanSetShutter'):
            self.client.openshutter()
        return True

    def closeShutter(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        if self.data.get('CanSetShutter'):
            self.client.closeshutter()
        return True

    def abortSlew(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.client.abortslew()
        return True
