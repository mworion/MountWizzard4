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

    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

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

        self.dataEntry(self.client.dew1, 'DEW_CURRENT.DEW_CURRENT_A')
        self.dataEntry(self.client.dew2, 'DEW_CURRENT.DEW_CURRENT_B')
        self.dataEntry(self.client.dew3, 'DEW_CURRENT.DEW_CURRENT_C')
        self.dataEntry(self.client.autodewon, 'AUTO_DEW.DEW_A')
        self.dataEntry(self.client.autodewon, 'AUTO_DEW.DEW_B')
        self.dataEntry(self.client.autodewon, 'AUTO_DEW.DEW_C')
        self.dataEntry(self.client.current, 'POWER_SENSORS.SENSOR_CURRENT')
        self.dataEntry(self.client.voltage, 'POWER_SENSORS.SENSOR_VOLTAGE')
        self.dataEntry(self.client.voltage, 'POWER_SENSORS.SENSOR_VOLTAGE')

        self.dataEntry(self.client.usbon, 'USB_HUB_CONTROL.INDI_ENABLED')
        self.dataEntry(self.client.usb1on, 'USB_PORT_CONTROL.PORT_1')
        self.dataEntry(self.client.usb2on, 'USB_PORT_CONTROL.PORT_2')
        self.dataEntry(self.client.usb3on, 'USB_PORT_CONTROL.PORT_3')
        self.dataEntry(self.client.usb4on, 'USB_PORT_CONTROL.PORT_4')
        self.dataEntry(self.client.usb5on, 'USB_PORT_CONTROL.PORT_5')
        self.dataEntry(self.client.usb6on, 'USB_PORT_CONTROL.PORT_6')

        self.dataEntry(self.client.power1on, 'POWER_CONTROL.POWER_CONTROL_1')
        self.dataEntry(self.client.power2on, 'POWER_CONTROL.POWER_CONTROL_2')
        self.dataEntry(self.client.power3on, 'POWER_CONTROL.POWER_CONTROL_3')
        self.dataEntry(self.client.power4on, 'POWER_CONTROL.POWER_CONTROL_4')

        return True
