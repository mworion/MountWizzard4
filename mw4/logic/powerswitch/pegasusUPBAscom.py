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

    CYCLE_POLL_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

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

        model = 'UPB' if self.client.maxswitch == 15 else 'UPBv2'

        self.data['FIRMWARE_INFO.VERSION'] = '1.4' if model == 'UPB' else '2.1'
        if model == 'UPB':
            self.dataEntry(self.client.getswitch(0), 'POWER_CONTROL.POWER_CONTROL_1')
            self.dataEntry(self.client.getswitch(1), 'POWER_CONTROL.POWER_CONTROL_2')
            self.dataEntry(self.client.getswitch(2), 'POWER_CONTROL.POWER_CONTROL_3')
            self.dataEntry(self.client.getswitch(3), 'POWER_CONTROL.POWER_CONTROL_4')
            self.dataEntry(self.client.getswitchvalue(4), 'DEW_CURRENT.DEW_CURRENT_A')
            self.dataEntry(self.client.getswitchvalue(5), 'DEW_CURRENT.DEW_CURRENT_B')
            self.dataEntry(self.client.getswitch(6), 'USB_HUB_CONTROL.INDI_ENABLED')
            self.dataEntry(self.client.getswitch(7), 'AUTO_DEW.INDI_ENABLED')
            self.dataEntry(self.client.getswitchvalue(11), 'POWER_SENSORS.SENSOR_VOLTAGE')
            self.dataEntry(self.client.getswitchvalue(12), 'POWER_SENSORS.SENSOR_CURRENT')
            self.dataEntry(self.client.getswitchvalue(13), 'POWER_SENSORS.SENSOR_POWER')

        if model == 'UPBv2':
            self.dataEntry(self.client.getswitch(0), 'POWER_CONTROL.POWER_CONTROL_1')
            self.dataEntry(self.client.getswitch(1), 'POWER_CONTROL.POWER_CONTROL_2')
            self.dataEntry(self.client.getswitch(2), 'POWER_CONTROL.POWER_CONTROL_3')
            self.dataEntry(self.client.getswitch(3), 'POWER_CONTROL.POWER_CONTROL_4')
            self.dataEntry(self.client.getswitchvalue(4) / 2.55, 'DEW_PWM.DEW_A')
            self.dataEntry(self.client.getswitchvalue(5) / 2.55, 'DEW_PWM.DEW_B')
            self.dataEntry(self.client.getswitchvalue(6) / 2.55, 'DEW_PWM.DEW_C')
            self.dataEntry(self.client.getswitch(7), 'USB_PORT_CONTROL.PORT_1')
            self.dataEntry(self.client.getswitch(8), 'USB_PORT_CONTROL.PORT_2')
            self.dataEntry(self.client.getswitch(9), 'USB_PORT_CONTROL.PORT_3')
            self.dataEntry(self.client.getswitch(10), 'USB_PORT_CONTROL.PORT_4')
            self.dataEntry(self.client.getswitch(11), 'USB_PORT_CONTROL.PORT_5')
            self.dataEntry(self.client.getswitch(12), 'USB_PORT_CONTROL.PORT_6')
            self.dataEntry(self.client.getswitch(13), 'AUTO_DEW.DEW_A')
            self.dataEntry(self.client.getswitch(13), 'AUTO_DEW.DEW_B')
            self.dataEntry(self.client.getswitch(13), 'AUTO_DEW.DEW_C')
            self.dataEntry(self.client.getswitchvalue(17), 'POWER_SENSORS.SENSOR_VOLTAGE')
            self.dataEntry(self.client.getswitchvalue(18), 'POWER_SENSORS.SENSOR_CURRENT')
            self.dataEntry(self.client.getswitchvalue(19), 'POWER_SENSORS.SENSOR_POWER')

        return True
