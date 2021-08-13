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
from base.alpacaBase import Switch


class PegasusUPBAlpaca(AlpacaClass):
    """
    """

    __all__ = ['PegasusUPBAlpaca',
               ]

    CYCLE_POLL_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.client = Switch()
        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().getInitialConfig()
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        model = 'UPB' if self.client.maxswitch() == 15 else 'UPBv2'

        self.data['FIRMWARE_INFO.VERSION'] = '1.4' if model == 'UPB' else '2.1'
        if model == 'UPB':
            self.data['POWER_CONTROL.POWER_CONTROL_1'] = self.client.getswitch(Id=0)
            self.data['POWER_CONTROL.POWER_CONTROL_2'] = self.client.getswitch(Id=1)
            self.data['POWER_CONTROL.POWER_CONTROL_3'] = self.client.getswitch(Id=2)
            self.data['POWER_CONTROL.POWER_CONTROL_4'] = self.client.getswitch(Id=3)
            self.data['DEW_CURRENT.DEW_CURRENT_A'] = self.client.getswitchvalue(Id=4)
            self.data['DEW_CURRENT.DEW_CURRENT_B'] = self.client.getswitchvalue(Id=5)
            self.data['USB_HUB_CONTROL.INDI_ENABLED'] = self.client.getswitch(Id=6)
            self.data['AUTO_DEW.INDI_ENABLED'] = self.client.getswitch(Id=7)
            self.data['POWER_SENSORS.SENSOR_VOLTAGE'] = self.client.getswitchvalue(Id=11)
            self.data['POWER_SENSORS.SENSOR_CURRENT'] = self.client.getswitchvalue(Id=12)
            self.data['POWER_SENSORS.SENSOR_POWER'] = self.client.getswitchvalue(Id=13)

        if model == 'UPBv2':
            self.data['POWER_CONTROL.POWER_CONTROL_1'] = self.client.getswitch(Id=0)
            self.data['POWER_CONTROL.POWER_CONTROL_2'] = self.client.getswitch(Id=1)
            self.data['POWER_CONTROL.POWER_CONTROL_3'] = self.client.getswitch(Id=2)
            self.data['POWER_CONTROL.POWER_CONTROL_4'] = self.client.getswitch(Id=3)
            self.data['DEW_PWM.DEW_A'] = self.client.getswitchvalue(Id=4) / 2.55
            self.data['DEW_PWM.DEW_B'] = self.client.getswitchvalue(Id=5) / 2.55
            self.data['DEW_PWM.DEW_C'] = self.client.getswitchvalue(Id=6) / 2.55
            self.data['USB_PORT_CONTROL.PORT_1'] = self.client.getswitch(Id=7)
            self.data['USB_PORT_CONTROL.PORT_2'] = self.client.getswitch(Id=8)
            self.data['USB_PORT_CONTROL.PORT_3'] = self.client.getswitch(Id=9)
            self.data['USB_PORT_CONTROL.PORT_4'] = self.client.getswitch(Id=10)
            self.data['USB_PORT_CONTROL.PORT_5'] = self.client.getswitch(Id=11)
            self.data['USB_PORT_CONTROL.PORT_6'] = self.client.getswitch(Id=12)
            self.data['AUTO_DEW.DEW_A'] = self.client.getswitch(Id=13)
            self.data['AUTO_DEW.DEW_B'] = self.client.getswitch(Id=13)
            self.data['AUTO_DEW.DEW_C'] = self.client.getswitch(Id=13)
            self.data['POWER_SENSORS.SENSOR_VOLTAGE'] = self.client.getswitchvalue(Id=17)
            self.data['POWER_SENSORS.SENSOR_CURRENT'] = self.client.getswitchvalue(Id=18)
            self.data['POWER_SENSORS.SENSOR_POWER'] = self.client.getswitchvalue(Id=19)

        return True

    def togglePowerPort(self, port=None):
        if not self.deviceConnected:
            return False
        if port is None:
            return False

        switchNumber = int(port) - 1
        val = self.data.get(f'POWER_CONTROL.POWER_CONTROL_{port}', True)
        self.client.setswitchvalue(Id=switchNumber, Value=not val)
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

        model = 'UPB' if self.client.maxswitch() == 15 else 'UPBv2'
        if model == 'UPBv2':
            switchNumber = int(port) + 6
            val = self.data.get(f'USB_PORT_CONTROL.PORT_{port}', True)
            self.client.setswitchvalue(Id=switchNumber, Value=val)
        return True

    def toggleAutoDew(self):
        if not self.deviceConnected:
            return False

        model = 'UPB' if self.client.maxswitch() == 15 else 'UPBv2'
        if model == 'UPB':
            val = self.data.get('AUTO_DEW.INDI_ENABLED', False)
            self.client.setswitchvalue(Id=7, Value=val)
        else:
            val = self.data.get('AUTO_DEW.DEW_A', False)
            self.client.setswitchvalue(Id=13, Value=val)
        return True

    def sendDew(self, port=None, value=None):
        if not self.deviceConnected:
            return False
        if port is None:
            return False
        if value is None:
            return False

        model = 'UPB' if self.client.maxswitch() == 15 else 'UPBv2'
        switchNumber = ord(port) - ord('A') + 4
        val = int(value * 2.55)
        if model == 'UPBv2':
            self.client.setswitchvalue(Id=switchNumber, Value=val)
        return True

    def sendAdjustableOutput(self, value=None):
        if not self.deviceConnected:
            return False
        return True

    def reboot(self):
        if not self.deviceConnected:
            return False
        return True
