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
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class PegasusUPBAscom(AscomClass):
    """
    """

    __all__ = ['PegasusUPBAscom',
               ]

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        maxSwitch = self.getAscomProperty('maxswitch')
        model = 'UPB' if maxSwitch == 15 else 'UPBv2'

        self.data['FIRMWARE_INFO.VERSION'] = '1.4' if model == 'UPB' else '2.1'
        if model == 'UPB':
            self.getAndStoreAscomProperty('getswitch(0)', 'POWER_CONTROL.POWER_CONTROL_1')
            self.getAndStoreAscomProperty('getswitch(1)', 'POWER_CONTROL.POWER_CONTROL_2')
            self.getAndStoreAscomProperty('getswitch(2)', 'POWER_CONTROL.POWER_CONTROL_3')
            self.getAndStoreAscomProperty('getswitch(3)', 'POWER_CONTROL.POWER_CONTROL_4')
            self.getAndStoreAscomProperty('getswitchvalue(4)', 'DEW_CURRENT.DEW_CURRENT_A')
            self.getAndStoreAscomProperty('getswitchvalue(5)', 'DEW_CURRENT.DEW_CURRENT_B')
            self.getAndStoreAscomProperty('getswitch(6)', 'USB_HUB_CONTROL.INDI_ENABLED')
            self.getAndStoreAscomProperty('getswitch(7)', 'AUTO_DEW.INDI_ENABLED')
            self.getAndStoreAscomProperty('getswitchvalue(11)', 'POWER_SENSORS.SENSOR_VOLTAGE')
            self.getAndStoreAscomProperty('getswitchvalue(12)', 'POWER_SENSORS.SENSOR_CURRENT')
            self.getAndStoreAscomProperty('getswitchvalue(13)', 'POWER_SENSORS.SENSOR_POWER')

        if model == 'UPBv2':
            self.getAndStoreAscomProperty('getswitch(0)', 'POWER_CONTROL.POWER_CONTROL_1')
            self.getAndStoreAscomProperty('getswitch(1)', 'POWER_CONTROL.POWER_CONTROL_2')
            self.getAndStoreAscomProperty('getswitch(2)', 'POWER_CONTROL.POWER_CONTROL_3')
            self.getAndStoreAscomProperty('getswitch(3)', 'POWER_CONTROL.POWER_CONTROL_4')
            self.getAndStoreAscomProperty('getswitchvalue(4) / 2.55', 'DEW_PWM.DEW_A')
            self.getAndStoreAscomProperty('getswitchvalue(5) / 2.55', 'DEW_PWM.DEW_B')
            self.getAndStoreAscomProperty('getswitchvalue(6) / 2.55', 'DEW_PWM.DEW_C')
            self.getAndStoreAscomProperty('getswitch(7)', 'USB_PORT_CONTROL.PORT_1')
            self.getAndStoreAscomProperty('getswitch(8)', 'USB_PORT_CONTROL.PORT_2')
            self.getAndStoreAscomProperty('getswitch(9)', 'USB_PORT_CONTROL.PORT_3')
            self.getAndStoreAscomProperty('getswitch(10)', 'USB_PORT_CONTROL.PORT_4')
            self.getAndStoreAscomProperty('getswitch(11)', 'USB_PORT_CONTROL.PORT_5')
            self.getAndStoreAscomProperty('getswitch(12)', 'USB_PORT_CONTROL.PORT_6')
            self.getAndStoreAscomProperty('getswitch(13)', 'AUTO_DEW.DEW_A')
            self.getAndStoreAscomProperty('getswitch(13)', 'AUTO_DEW.DEW_B')
            self.getAndStoreAscomProperty('getswitch(13)', 'AUTO_DEW.DEW_C')
            self.getAndStoreAscomProperty('getswitchvalue(17) / 10', 'POWER_SENSORS.SENSOR_VOLTAGE')
            self.getAndStoreAscomProperty('getswitchvalue(18) / 10', 'POWER_SENSORS.SENSOR_CURRENT')
            self.getAndStoreAscomProperty('getswitchvalue(19)', 'POWER_SENSORS.SENSOR_POWER')
        return True

    def togglePowerPort(self, port=None):
        if not self.deviceConnected:
            return False
        if port is None:
            return False

        switchNumber = int(port) - 1
        val = self.data.get(f'POWER_CONTROL.POWER_CONTROL_{port}', True)
        self.callAscomMethod('setswitch', (switchNumber, not val))
        return True

    def togglePowerPortBoot(self, port=None):
        if not self.deviceConnected:
            return False
        return True

    def toggleHubUSB(self):
        if not self.deviceConnected:
            return False
        return True

    def togglePortUSB(self, port=None):
        if not self.deviceConnected:
            return False
        if port is None:
            return False

        maxSwitch = self.getAscomProperty('maxswitch')
        model = 'UPB' if maxSwitch == 15 else 'UPBv2'
        if model == 'UPBv2':
            switchNumber = int(port) + 6
            val = self.data.get(f'USB_PORT_CONTROL.PORT_{port}', True)
            self.callAscomMethod('setswitch', (switchNumber, not val))
        return True

    def toggleAutoDew(self):
        if not self.deviceConnected:
            return False

        maxSwitch = self.getAscomProperty('maxswitch')
        model = 'UPB' if maxSwitch == 15 else 'UPBv2'

        if model == 'UPB':
            val = self.data.get('AUTO_DEW.INDI_ENABLED', False)
            self.callAscomMethod('setswitch', (7, not val))
        else:
            val = self.data.get('AUTO_DEW.DEW_A', False)
            self.callAscomMethod('setswitch', (13, not val))
        return True

    def sendDew(self, port=None, value=None):
        if not self.deviceConnected:
            return False
        if port is None:
            return False
        if value is None:
            return False

        maxSwitch = self.getAscomProperty('maxswitch')
        model = 'UPB' if maxSwitch == 15 else 'UPBv2'

        switchNumber = ord(port) - ord('A') + 4
        val = int(value * 2.55)
        if model == 'UPBv2':
            self.callAscomMethod('setswitchvalue', (switchNumber, val))
        return True

    def sendAdjustableOutput(self, value=None):
        if not self.deviceConnected:
            return False
        return True

    def reboot(self):
        if not self.deviceConnected:
            return False
        return True
