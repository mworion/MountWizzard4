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
# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.base.indiClass import IndiClass


class PegasusUPBIndi(IndiClass):
    """
    the class PegasusUPBIndi inherits all information and handling of the PegasusUPB device

        >>> power = PegasusUPBIndi(app=None)
    """

    __all__ = ['PegasusUPBIndi',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data
        self.data['VERSION.UPB'] = 0

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

        # only version 2 has 3 dew heaters
        if 'AUTO_DEW.DEW_C' in self.data:
            if self.data.get('VERSION.UPB', 1) != 2:
                self.data['VERSION.UPB'] = 2
                self.signals.version.emit(2)
                print('version 2')

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

        # this combination only exists in version 1
        if 'AUTO_DEW.AUTO_DEW_ENABLED' in self.data:
            if self.data.get('VERSION.UPB', 2) != 1:
                print('version 1')
                self.data['VERSION.UPB'] = 1
                self.signals.version.emit(1)
                print('version 1')

        return True

    def togglePowerPort(self, port=None):
        """
        togglePowerPort

        :param port:
        :return: true for test purpose
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
        :return: true for test purpose
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

        :return: true for test purpose
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
        :return: true for test purpose
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

    def toggleAutoDew(self):
        """
        toggleAutoDew

        :return: true for test purpose
        """

        if self.device is None:
            return False

        autoDew = self.device.getSwitch('AUTO_DEW')
        autoDew['AUTO_DEW_ENABLED'] = not autoDew['AUTO_DEW_ENABLED']
        autoDew['AUTO_DEW_DISABLED'] = not autoDew['AUTO_DEW_DISABLED']
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='AUTO_DEW',
                                        elements=autoDew,
                                        )
        return suc

    def toggleAutoDewPort(self, port=None):
        """
        toggleAutoDewPort

        :param port:
        :return: true for test purpose
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
