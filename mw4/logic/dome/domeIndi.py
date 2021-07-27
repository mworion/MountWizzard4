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
from base.indiClass import IndiClass


class DomeIndi(IndiClass):
    """
    the class Dome inherits all information and handling of the Dome device.
    There will be some parameters who will define the slewing position of the
    dome relating to the mount.

        >>> dome = DomeIndi(app=None)
    """

    __all__ = ['DomeIndi',
               ]

    UPDATE_RATE = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data
        self.lastAzimuth = None

        self.app.update1s.connect(self.updateStatus)

    def setUpdateConfig(self, deviceName):
        """
        setUpdateRate corrects the update rate of dome devices to get an
        defined setting regardless, what is setup in server side.

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
        updateStatus emits the actual azimuth status every 3 second in case of
        opening a window and get the signals late connected as INDI does not
        repeat any signal of it's own

        :return: true for test purpose
        """
        if not self.client.connected:
            return False

        azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION', 0)
        self.signals.azimuth.emit(azimuth)
        return True

    def updateNumber(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it
        runs through the device list and writes the number data to the according
        locations.

        :param deviceName:
        :param propertyName:
        :return:
        """
        if not super().updateNumber(deviceName, propertyName):
            return False

        for element, value in self.device.getNumber(propertyName).items():

            if element == 'DOME_ABSOLUTE_POSITION':
                azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION',
                                        0)
                self.signals.azimuth.emit(azimuth)

                slewing = self.device.ABS_DOME_POSITION['state'] == 'Busy'
                self.data['Slewing'] = slewing

            if element == 'SHUTTER_OPEN':
                moving = self.device.DOME_SHUTTER['state'] == 'Busy'
                if moving:
                    self.data['Shutter.Status'] = 'Moving'
                else:
                    self.data['Shutter.Status'] = '-'

        return True

    def slewToAltAz(self, altitude=0, azimuth=0):
        """
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
        return suc

    def openShutter(self):
        """
        :return: success
        """
        if self.device is None:
            return False

        if self.deviceName is None or not self.deviceName:
            return False

        position = self.device.getSwitch('DOME_SHUTTER')

        if 'SHUTTER_OPEN' not in position:
            return False

        position['SHUTTER_OPEN'] = 'On'
        position['SHUTTER_CLOSE'] = 'Off'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='DOME_SHUTTER',
                                        elements=position,
                                        )
        return suc

    def closeShutter(self):
        """
        :return: success
        """
        if self.device is None:
            return False

        if self.deviceName is None or not self.deviceName:
            return False

        position = self.device.getSwitch('DOME_SHUTTER')

        if 'SHUTTER_CLOSE' not in position:
            return False

        position['SHUTTER_OPEN'] = 'Off'
        position['SHUTTER_CLOSE'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='DOME_SHUTTER',
                                        elements=position,
                                        )
        return suc

    def abortSlew(self):
        """
        :return: success
        """
        if self.device is None:
            return False

        if self.deviceName is None or not self.deviceName:
            return False

        position = self.device.getSwitch('DOME_ABORT_MOTION')

        if 'ABORT' not in position:
            return False

        position['ABORT'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='DOME_ABORT_MOTION',
                                        elements=position,
                                        )
        return suc
