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
from mw4.base import indiClass


class PegasusUPBSignals(PyQt5.QtCore.QObject):
    """
    The PegasusUPBSignals class offers a list of signals to be used and instantiated by
    the PegasusUPB class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['PegasusUPBSignals']

    version = PyQt5.QtCore.pyqtSignal(int)


class PegasusUPB(indiClass.IndiClass):
    """
    the class PegasusUPB inherits all information and handling of the PegasusUPB device

        >>> power = PegasusUPB(app=None)
    """

    __all__ = ['PegasusUPB',
               ]

    logger = logging.getLogger(__name__)

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

    def __init__(self, app=None):
        super().__init__(app=app)

        self.versionUPB = 0
        self.signals = PegasusUPBSignals()

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of weather devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """

        if deviceName != self.name:
            return False

        if self.device is None:
            return False

        # setting polling updates in driver

        update = self.device.getNumber('POLLING')

        if 'PERIOD' not in update:
            return False

        if update.get('PERIOD', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING',
                                        elements=update,
                                        )

        return suc

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
            # only version 2 has 3 dew heaters
            if element == 'DEW_C':
                if self.versionUPB != 2:
                    self.versionUPB = 2
                    self.signals.version.emit(2)

        return True

    def updateSwitch(self, deviceName, propertyName):
        """
        updateSwitch is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """

        if not super().updateSwitch(deviceName, propertyName):
            return False

        for element, value in self.device.getSwitch(propertyName).items():
            # this combination only exists in version 1
            if propertyName == 'AUTO_DEW' and element == 'AUTO_DEW_ENABLED':
                if self.versionUPB != 1:
                    self.versionUPB = 1
                    self.signals.version.emit(1)

        return True

    def togglePowerPort(self, port=None):
        """
        togglePowerPort

        :param port:
        :return: true fot test purpose
        """

        if port is None:
            return False

        if self.device is None:
            return False

        power = self.device.getSwitch('POWER_CONTROL')
        portName = f'POWER_CONTROL_{port}'
        if portName not in power:
            return False

        power[portName] = not power[portName]
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='POWER_CONTROL',
                                        elements=power,
                                        )
        return suc

    def togglePowerPortBoot(self, port=None):
        """
        togglePowerPortBoot

        :param port:
        :return: true fot test purpose
        """

        if port is None:
            return False

        if self.device is None:
            return False

        power = self.device.getSwitch('POWER_ON_BOOT')
        portName = f'POWER_PORT_{port}'
        if portName not in power:
            return False

        power[portName] = not power[portName]
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='POWER_ON_BOOT',
                                        elements=power,
                                        )
        return suc

    def toggleHubUSB(self):
        """
        toggleHubUSB

        :return: true fot test purpose
        """

        if self.device is None:
            return False

        usb = self.device.getSwitch('USB_HUB_CONTROL')
        if 'ENABLED' not in usb:
            return False
        if 'DISABLED' not in usb:
            return False

        usb['ENABLED'] = not usb['ENABLED']
        usb['DISABLED'] = not usb['DISABLED']
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='USB_HUB_CONTROL',
                                        elements=usb,
                                        )
        return suc

    def togglePortUSB(self, port=None):
        """
        togglePortUSB

        :param port:
        :return: true fot test purpose
        """

        if port is None:
            return False

        if self.device is None:
            return False

        usb = self.device.getSwitch('USB_PORT_CONTROL')

        portName = f'PORT_{port}'
        if portName not in usb:
            return False

        usb[portName] = not usb[portName]
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='USB_PORT_CONTROL',
                                        elements=usb,
                                        )
        return suc

    def sendAutoDew(self, value=False):
        """
        sendAutoDew

        :param value:
        :return: true fot test purpose
        """

        if self.device is None:
            return False

        autoDew = self.device.getSwitch('AUTO_DEW')
        autoDew['AUTO_DEW_ENABLED'] = value
        autoDew['AUTO_DEW_DISABLED'] = not value
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='AUTO_DEW',
                                        elements=autoDew,
                                        )
        return suc

    def toggleAutoDewPort(self, port=None):
        """
        toggleAutoDewPort

        :param port:
        :return: true fot test purpose
        """

        if port is None:
            return False

        if self.device is None:
            return False

        autoDew = self.device.getSwitch('AUTO_DEW')
        portName = f'DEW_{port}'

        if portName not in autoDew:
            return False

        autoDew[portName] = not autoDew[portName]
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='AUTO_DEW',
                                        elements=autoDew,
                                        )
        return suc

    def sendDew(self, port='', value=None):
        """

        :param port:
        :param value:
        :return: success
        """

        if self.device is None:
            return False

        dew = self.device.getNumber('DEW_PWM')
        dew[f'DEW_{port}'] = value
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='DEW_PWM',
                                        elements=dew,
                                        )
        return suc

    def sendAdjustableOutput(self, value=None):
        """

        :param value:
        :return: success
        """

        if self.device is None:
            return False

        output = self.device.getNumber('ADJUSTABLE_VOLTAGE')
        output['ADJUSTABLE_VOLTAGE_VALUE'] = value
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='ADJUSTABLE_VOLTAGE',
                                        elements=output,
                                        )
        return suc
