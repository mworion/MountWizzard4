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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.alpacaClass import AlpacaClass


class DomeAlpaca(AlpacaClass):
    """
    """

    __all__ = ['DomeAlpaca']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        self.getAndStoreAlpacaProperty('cansetaltitude', 'CanSetAltitude')
        self.getAndStoreAlpacaProperty('cansetazimuth', 'CanSetAzimuth')
        self.getAndStoreAlpacaProperty('cansetshutter', 'CanSetShutter')
        self.log.debug(f'Initial data: {self.data}')
        return True

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
        azimuth = self.getAlpacaProperty('azimuth')
        self.storePropertyToData(azimuth, 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION')
        self.signals.azimuth.emit(azimuth)
        self.getAndStoreAlpacaProperty('slewing', 'Slewing')

        state = self.getAlpacaProperty('shutterstatus')
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
            self.setAlpacaProperty('slewtoazimuth', Azimuth=azimuth)
        if self.data.get('CanSetAltitude'):
            self.setAlpacaProperty('slewtoaltitude', Altitude=altitude)
        return True

    def openShutter(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        if self.data.get('CanSetShutter'):
            self.getAlpacaProperty('openshutter')
        return True

    def closeShutter(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        if self.data.get('CanSetShutter'):
            self.getAlpacaProperty('closeshutter')
        return True

    def slewCW(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False
        return True

    def slewCCW(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False
        return True

    def abortSlew(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.getAlpacaProperty('abortslew')
        return True
