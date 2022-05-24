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
from base.alpacaClass import AlpacaClass


class PegasusUPBAlpaca(AlpacaClass):
    """
    """

    __all__ = ['PegasusUPBAlpaca',
               ]

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)

        self.signals = signals
        self.data = data

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        model = 'UPB' if self.getAlpacaProperty('maxswitch') == 15 else 'UPBv2'

        self.data['FIRMWARE_INFO.VERSION'] = '1.4' if model == 'UPB' else '2.1'
        if model == 'UPB':
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=0),
                                     'POWER_CONTROL.POWER_CONTROL_1')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=1),
                                     'POWER_CONTROL.POWER_CONTROL_2')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=2),
                                     'POWER_CONTROL.POWER_CONTROL_3')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=3),
                                     'POWER_CONTROL.POWER_CONTROL_4')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue', Id=4),
                                     'DEW_CURRENT.DEW_CURRENT_A')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue', Id=5),
                                     'DEW_CURRENT.DEW_CURRENT_B')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=6),
                                     'USB_HUB_CONTROL.INDI_ENABLED')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=7),
                                     'AUTO_DEW.INDI_ENABLED')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue', Id=11),
                                     'POWER_SENSORS.SENSOR_VOLTAGE')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue', Id=12),
                                     'POWER_SENSORS.SENSOR_CURRENT')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue', Id=13),
                                     'POWER_SENSORS.SENSOR_POWER')

        if model == 'UPBv2':
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=0),
                                     'POWER_CONTROL.POWER_CONTROL_1')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=1),
                                     'POWER_CONTROL.POWER_CONTROL_2')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=2),
                                     'POWER_CONTROL.POWER_CONTROL_3')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=3),
                                     'POWER_CONTROL.POWER_CONTROL_4')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue',
                                                            Id=4) / 2.55,
                                     'DEW_PWM.DEW_A')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue',
                                                            Id=5) / 2.55,
                                     'DEW_PWM.DEW_B')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue',
                                                            Id=6) / 2.55,
                                     'DEW_PWM.DEW_C')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=7),
                                     'USB_PORT_CONTROL.PORT_1')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=8),
                                     'USB_PORT_CONTROL.PORT_2')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=9),
                                     'USB_PORT_CONTROL.PORT_3')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=10),
                                     'USB_PORT_CONTROL.PORT_4')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=11),
                                     'USB_PORT_CONTROL.PORT_5')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=12),
                                     'USB_PORT_CONTROL.PORT_6')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=13),
                                     'AUTO_DEW.DEW_A')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=13),
                                     'AUTO_DEW.DEW_B')
            self.storePropertyToData(self.getAlpacaProperty('getswitch', Id=13),
                                     'AUTO_DEW.DEW_C')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue', Id=17),
                                     'POWER_SENSORS.SENSOR_VOLTAGE')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue', Id=18),
                                     'POWER_SENSORS.SENSOR_CURRENT')
            self.storePropertyToData(self.getAlpacaProperty('getswitchvalue', Id=19),
                                     'POWER_SENSORS.SENSOR_POWER')

        return True

    def togglePowerPort(self, port=None):
        if not self.deviceConnected:
            return False
        if port is None:
            return False

        switchNumber = int(port) - 1
        val = self.data.get(f'POWER_CONTROL.POWER_CONTROL_{port}', True)
        self.setAlpacaProperty('setswitchvalue', Id=switchNumber, Value=not val)
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

        model = 'UPB' if self.getAlpacaProperty('maxswitch') == 15 else 'UPBv2'
        if model == 'UPBv2':
            switchNumber = int(port) + 6
            val = self.data.get(f'USB_PORT_CONTROL.PORT_{port}', True)
            self.setAlpacaProperty('setswitchvalue', Id=switchNumber, Value=val)
        return True

    def toggleAutoDew(self):
        if not self.deviceConnected:
            return False

        model = 'UPB' if self.getAlpacaProperty('maxswitch') == 15 else 'UPBv2'
        if model == 'UPB':
            val = self.data.get('AUTO_DEW.INDI_ENABLED', False)
            self.setAlpacaProperty('setswitchvalue', Id=7, Value=val)
        else:
            val = self.data.get('AUTO_DEW.DEW_A', False)
            self.setAlpacaProperty('setswitchvalue', Id=13, Value=val)
        return True

    def sendDew(self, port=None, value=None):
        if not self.deviceConnected:
            return False
        if port is None:
            return False
        if value is None:
            return False

        model = 'UPB' if self.getAlpacaProperty('maxswitch') == 15 else 'UPBv2'
        switchNumber = ord(port) - ord('A') + 4
        val = int(value * 2.55)
        if model == 'UPBv2':
            self.setAlpacaProperty('setswitchvalue', Id=switchNumber, Value=val)
        return True

    def sendAdjustableOutput(self, value=None):
        if not self.deviceConnected:
            return False
        return True

    def reboot(self):
        if not self.deviceConnected:
            return False
        return True
