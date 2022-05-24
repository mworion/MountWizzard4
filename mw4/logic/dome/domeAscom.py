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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class DomeAscom(AscomClass):
    """
    """

    __all__ = ['DomeAscom']

    shutterStates = ['Open', 'Closed', 'Opening', 'Closing', 'Error']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        self.getAndStoreAscomProperty('CanSetAltitude', 'CanSetAltitude')
        self.getAndStoreAscomProperty('CanSetAzimuth', 'CanSetAzimuth')
        self.getAndStoreAscomProperty('CanSetShutter', 'CanSetShutter')
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
        azimuth = self.getAscomProperty('Azimuth')
        self.storePropertyToData(azimuth, 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION')
        self.signals.azimuth.emit(azimuth)
        self.getAndStoreAscomProperty('Slewing', 'Slewing')

        state = self.getAscomProperty('ShutterStatus')
        if state == 0:
            stateText = self.shutterStates[state]
            self.storePropertyToData(stateText, 'Status.Shutter')
            self.storePropertyToData(True,
                                     'DOME_SHUTTER.SHUTTER_OPEN',
                                     elementInv='DOME_SHUTTER.SHUTTER_CLOSED')
        elif state == 1:
            stateText = self.shutterStates[state]
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
        :param altitude:
        :param azimuth:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.SlewToAzimuth, azimuth)
        self.callMethodThreaded(self.client.SlewToAltitude, altitude)
        return True

    def openShutter(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.OpenShutter)
        return True

    def closeShutter(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.CloseShutter)
        return True

    def slewCW(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.OpenShutter)
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
        return True
