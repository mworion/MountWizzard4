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
from base.indiClass import IndiClass


class PegasusUPBIndi(IndiClass):
    """
    the class PegasusUPBIndi inherits all information and handling of the PegasusUPB device

        >>> power = PegasusUPBIndi(app=None)
    """

    __all__ = ['PegasusUPBIndi',
               ]

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data)
        self.modelVersion = 0

    def setUpdateConfig(self, deviceName):
        """
        :param deviceName:
        :return: success
        """
        if not super().setUpdateConfig(deviceName):
            return False

        update = self.device.getNumber('POLLING')
        update['PERIOD'] = self.updateRate
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING',
                                        elements=update)
        self.log.info(f'Polling [{deviceName}] success: [{suc}]')
        return suc

    def updateText(self, deviceName, propertyName):
        """
        :param deviceName:
        :param propertyName:
        :return:
        """
        if not super().updateText(deviceName, propertyName):
            return False
        if propertyName != 'DRIVER_INFO' and propertyName != 'FIRMWARE_INFO':
            return False
        if 'DRIVER_INFO.DEVICE_MODEL' in self.data:
            if self.data.get('DRIVER_INFO.DEVICE_MODEL', 'UPB') == 'UPB':
                if self.modelVersion != 1:
                    self.signals.version.emit(1)
                self.modelVersion = 1
            else:
                if self.modelVersion != 2:
                    self.signals.version.emit(2)
                self.modelVersion = 2

        if 'FIRMWARE_INFO.VERSION' in self.data:
            if self.data.get('FIRMWARE_INFO.VERSION', '1.4') < '1.5':
                if self.modelVersion != 1:
                    self.signals.version.emit(1)
                self.modelVersion = 1
            else:
                if self.modelVersion != 2:
                    self.signals.version.emit(2)
                self.modelVersion = 2
        return True

    def togglePowerPort(self, port=None):
        """
        :param port:
        :return: true for test purpose
        """
        if port is None:
            return False
        if self.device is None:
            return False
        if self.isINDIGO:
            propertyName = 'AUX_POWER_OUTLET'
            power = self.device.getSwitch(propertyName)
            portName = f'OUTLET_{port}'
        else:
            propertyName = 'POWER_CONTROL'
            power = self.device.getSwitch(propertyName)
            portName = f'POWER_CONTROL_{port}'

        if portName not in power:
            return False

        if power[portName] == 'On':
            power[portName] = 'Off'
        else:
            power[portName] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName=propertyName,
                                        elements=power,
                                        )
        return suc

    def togglePowerPortBoot(self, port=None):
        """
        :param port:
        :return: true for test purpose
        """
        if port is None:
            return False
        if self.device is None:
            return False
        if self.isINDIGO:
            return False
        else:
            propertyName = 'POWER_ON_BOOT'
            power = self.device.getSwitch(propertyName)
            portName = f'POWER_PORT_{port}'

        if portName not in power:
            return False

        if power[portName] == 'On':
            power[portName] = 'Off'
        else:
            power[portName] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName=propertyName,
                                        elements=power,
                                        )
        return suc

    def toggleHubUSB(self):
        """
        :return: true for test purpose
        """
        if self.device is None:
            return False
        if self.isINDIGO:
            return False
        else:
            propertyName = 'USB_HUB_CONTROL'
            usb = self.device.getSwitch(propertyName)
            if 'INDI_ENABLED' not in usb:
                return False
            if usb['INDI_ENABLED'] == 'On':
                usb['INDI_ENABLED'] = 'Off'
                usb['INDI_DISABLED'] = 'On'
            else:
                usb['INDI_ENABLED'] = 'On'
                usb['INDI_DISABLED'] = 'Off'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName=propertyName,
                                        elements=usb,
                                        )
        return suc

    def togglePortUSB(self, port=None):
        """
        :param port:
        :return: true for test purpose
        """
        if port is None:
            return False
        if self.device is None:
            return False
        if self.isINDIGO:
            propertyName = 'AUX_USB_PORT'
            usb = self.device.getSwitch(propertyName)
            portName = f'PORT_{port}'
        else:
            propertyName = 'USB_PORT_CONTROL'
            usb = self.device.getSwitch(propertyName)
            portName = f'PORT_{port}'

        if portName not in usb:
            return False

        if usb[portName] == 'On':
            usb[portName] = 'Off'
        else:
            usb[portName] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName=propertyName,
                                        elements=usb,
                                        )
        return suc

    def toggleAutoDew(self):
        """
        :return: true for test purpose
        """
        if self.device is None:
            return False
        if self.isINDIGO:
            propertyName = 'AUX_DEW_CONTROL'
            autoDew = self.device.getSwitch(propertyName)

            if autoDew['MANUAL'] == 'On':
                autoDew['MANUAL'] = 'Off'
                autoDew['AUTOMATIC'] = 'On'
            else:
                autoDew['MANUAL'] = 'On'
                autoDew['AUTOMATIC'] = 'Off'
        else:
            propertyName = 'AUTO_DEW'
            autoDew = self.device.getSwitch(propertyName)

            if self.modelVersion == 1:
                if 'INDI_ENABLED' not in autoDew:
                    return False
                if autoDew['INDI_ENABLED'] == 'On':
                    autoDew['INDI_ENABLED'] = 'Off'
                    autoDew['INDI_DISABLED'] = 'On'
                else:
                    autoDew['INDI_ENABLED'] = 'Off'
                    autoDew['INDI_DISABLED'] = 'On'
            else:
                if 'DEW_A' not in autoDew:
                    return False
                if autoDew['DEW_A'] == 'On':
                    autoDew['DEW_A'] = 'Off'
                    autoDew['DEW_B'] = 'Off'
                    autoDew['DEW_C'] = 'Off'
                else:
                    autoDew['DEW_A'] = 'On'
                    autoDew['DEW_B'] = 'On'
                    autoDew['DEW_C'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName=propertyName,
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
        if self.isINDIGO:
            conv = {'A': '1', 'B': '2', 'C': '3'}
            propertyName = 'AUX_HEATER_OUTLET'
            dew = self.device.getNumber(propertyName)
            portName = f'OUTLET_{conv[port]}'
        else:
            propertyName = 'DEW_PWM'
            dew = self.device.getNumber(propertyName)
            portName = f'DEW_{port}'

        if portName not in dew:
            return False

        dew[portName] = value
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName=propertyName,
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
        if self.isINDIGO:
            propertyName = 'X_AUX_VARIABLE_POWER_OUTLET'
            output = self.device.getNumber(propertyName)
            portName = 'OUTLET_1'
        else:
            propertyName = 'ADJUSTABLE_VOLTAGE'
            output = self.device.getNumber(propertyName)
            portName = 'ADJUSTABLE_VOLTAGE_VALUE'

        output[portName] = value
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName=propertyName,
                                        elements=output,
                                        )
        return suc

    def reboot(self):
        """
        :return: success
        """
        if self.device is None:
            return False
        if self.isINDIGO:
            propertyName = 'X_AUX_REBOOT'
            output = self.device.getSwitch(propertyName)
            portName = 'REBOOT'
        else:
            propertyName = 'REBOOT_DEVICE'
            output = self.device.getSwitch(propertyName)
            portName = 'REBOOT'

        if portName not in output:
            return False

        output[portName] = 'On'
        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName=propertyName,
                                        elements=output,
                                        )
        return suc
