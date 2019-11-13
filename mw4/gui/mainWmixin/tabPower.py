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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import copy
# external packages
import PyQt5
# local import


class Power(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):

        self.powerOnOFF = {'1': self.ui.powerPort1,
                           '2': self.ui.powerPort2,
                           '3': self.ui.powerPort3,
                           '4': self.ui.powerPort4,
                           }
        self.powerBoot = {'1': self.ui.powerBootPort1,
                          '2': self.ui.powerBootPort2,
                          '3': self.ui.powerBootPort3,
                          '4': self.ui.powerBootPort4,
                          }
        self.dew = {'A': self.ui.dewA,
                    'B': self.ui.dewB,
                    'C': self.ui.dewC,
                    }

        signals = self.app.power.client.signals
        signals.newNumber.connect(self.updatePowerGui)
        signals.deviceDisconnected.connect(self.clearPowerGui)
        signals.newNumber.connect(self.setPowerNumber)
        signals.defNumber.connect(self.setPowerNumber)
        signals.newSwitch.connect(self.setPowerSwitch)
        signals.defSwitch.connect(self.setPowerSwitch)
        signals.newText.connect(self.setPowerText)
        signals.defText.connect(self.setPowerText)

        for name, button in self.dew.items():
            self.clickable(button).connect(self.setDew)
        for name, button in self.powerOnOFF.items():
            button.clicked.connect(self.togglePowerPort)
        for name, button in self.powerBoot.items():
            button.clicked.connect(self.togglePowerBootPort)

        self.ui.hubUSB.clicked.connect(self.toggleHubUSB)
        self.ui.autoDew.clicked.connect(self.setAutoDew)

    def initConfig(self):
        # config = self.app.config['mainW']
        return True

    def storeConfig(self):
        # config = self.app.config['mainW']
        return True

    def clearPowerGui(self):
        """
        clearPowerGui changes the state of the Pegasus values to '-'

        :return: success for test
        """

        self.ui.powerTemp.setText('-')
        self.ui.powerHumidity.setText('-')
        self.ui.powerDewPoint.setText('-')
        self.ui.powerCurrent1.setText('-')
        self.ui.powerCurrent2.setText('-')
        self.ui.powerCurrent3.setText('-')
        self.ui.powerCurrent4.setText('-')
        self.ui.consumptionAvgAmps.setText('-')
        self.ui.consumptionAmpHours.setText('-')
        self.ui.consumptionWattHours.setText('-')
        self.ui.sensorVoltage.setText('-')
        self.ui.sensorCurrent.setText('-')
        self.ui.sensorPower.setText('-')
        self.ui.dewCurrentA.setText('-')
        self.ui.dewCurrentB.setText('-')

        return True

    def updatePowerGui(self):
        """
        updatePowerGui changes the style of the button related to the state of the Pegasus

        :return: success for test
        """

        value = self.app.power.data.get('WEATHER_TEMPERATURE', 0)
        self.ui.powerTemp.setText('{0:4.1f}'.format(value))
        value = self.app.power.data.get('WEATHER_HUMIDITY', 0)
        self.ui.powerHumidity.setText('{0:3.0f}'.format(value))
        value = self.app.power.data.get('WEATHER_DEWPOINT', 0)
        self.ui.powerDewPoint.setText('{0:4.1f}'.format(value))

        value = self.app.power.data.get('POWER_CURRENT_1', 0)
        self.ui.powerCurrent1.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('POWER_CURRENT_2', 0)
        self.ui.powerCurrent2.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('POWER_CURRENT_3', 0)
        self.ui.powerCurrent3.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('POWER_CURRENT_4', 0)
        self.ui.powerCurrent4.setText('{0:4.2f}'.format(value))

        value = self.app.power.data.get('CONSUMPTION_AVG_AMPS', 0)
        self.ui.consumptionAvgAmps.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('CONSUMPTION_AMP_HOURS', 0)
        self.ui.consumptionAmpHours.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('CONSUMPTION_WATT_HOURS', 0)
        self.ui.consumptionWattHours.setText('{0:4.2f}'.format(value))

        value = self.app.power.data.get('SENSOR_VOLTAGE', 0)
        self.ui.sensorVoltage.setText('{0:4.1f}'.format(value))
        value = self.app.power.data.get('SENSOR_CURRENT', 0)
        self.ui.sensorCurrent.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('SENSOR_POWER', 0)
        self.ui.sensorPower.setText('{0:4.2f}'.format(value))

        value = self.app.power.data.get('DEW_CURRENT_A', 0)
        self.ui.dewCurrentA.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('DEW_CURRENT_B', 0)
        self.ui.dewCurrentB.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('DEW_CURRENT_C', 0)
        self.ui.dewCurrentC.setText('{0:4.2f}'.format(value))

        return True

    def setPowerNumber(self, deviceName, propertyName):
        """

        :param deviceName:
        :param propertyName:
        :return:
        """

        device = self.app.power.device
        name = self.app.power.name

        if device is None:
            return False
        if deviceName != name:
            return False
        if not getattr(device, 'getNumber', False):
            return False

        for element, value in device.getNumber(propertyName).items():
            if element == 'DEW_A':
                self.ui.dewA.setText(f'{value:3.0f}')
            elif element == 'DEW_B':
                self.ui.dewB.setText(f'{value:3.0f}')
            elif element == 'DEW_C':
                self.ui.dewC.setText(f'{value:3.0f}')
            # print(deviceName, propertyName, element, value)

        return True

    def setPowerSwitch(self, deviceName, propertyName):
        """

        :param deviceName:
        :param propertyName:
        :return:
        """

        device = self.app.power.device
        name = self.app.power.name

        if device is None:
            return False
        if deviceName != name:
            return False
        if not getattr(device, 'getSwitch', False):
            return False

        for element, value in device.getSwitch(propertyName).items():
            if element in self.powerOnOFF:
                if value:
                    self.changeStyleDynamic(self.powerOnOFF[element], 'running', True)
                else:
                    self.changeStyleDynamic(self.powerOnOFF[element], 'running', False)
            elif element in self.powerBoot:
                self.powerBoot[element].setChecked(value)
            elif propertyName == 'USB_HUB_CONTROL' and element == 'ENABLED':
                self.changeStyleDynamic(self.ui.hubUSB, 'running', value)
            elif propertyName == 'USB_HUB_CONTROL' and element == 'DISABLED':
                self.changeStyleDynamic(self.ui.hubUSB, 'running', not value)
            elif propertyName == 'AUTO_DEW' and element == 'AUTO_DEW_ENABLED':
                self.ui.autoDew.setChecked(value)
            # print(deviceName, propertyName, element, value)

        return True

    def setPowerText(self, deviceName, propertyName):
        """

        :param deviceName:
        :param propertyName:
        :return:
        """

        device = self.app.power.device
        name = self.app.power.name

        if device is None:
            return False
        if deviceName != name:
            return False
        if not getattr(device, 'getText', False):
            return False

        for element, value in device.getText(propertyName).items():
            if element == 'POWER_LABEL_1':
                self.ui.powerLabel1.setText(value)
            elif element == 'POWER_LABEL_2':
                self.ui.powerLabel2.setText(value)
            elif element == 'POWER_LABEL_3':
                self.ui.powerLabel3.setText(value)
            elif element == 'POWER_LABEL_4':
                self.ui.powerLabel4.setText(value)
            # print(deviceName, propertyName, element, value)

        return True

    def setDew(self):
        """

        :return: true fot test purpose
        """

        for name, button in self.dew.items():
            if button != self.sender():
                continue

            actValue = int(button.text())
            dlg = PyQt5.QtWidgets.QInputDialog()
            value, ok = dlg.getInt(self,
                                   f'Set dew PWM {name}',
                                   'Value (0-100):',
                                   actValue,
                                   0,
                                   100,
                                   10,
                                   )

            if not ok:
                return False

            suc = self.app.power.sendDew(port=name, value=value)
            return suc

    def togglePowerPort(self):
        """
        togglePowerPort  toggles the state of the power switch
        :return: success
        """

        for name, button in self.powerOnOFF.items():
            if button != self.sender():
                continue
            suc = self.app.power.togglePowerPort(port=int(name))
        return suc

    def togglePowerBootPort(self):
        """
        togglePowerPort  toggles the state of the power switch
        :return: success
        """

        for name, button in self.powerBoot.items():
            if button != self.sender():
                continue
            suc = self.app.power.togglePowerPortBoot(port=int(name))
        return suc

    def toggleHubUSB(self):
        """
        toggleHubUSB

        :return: true fot test purpose
        """
        suc = self.app.power.toggleHubUSB()
        return suc

    def setAutoDew(self):
        """
        setAutoDew

        :return: true fot test purpose
        """
        suc = self.app.power.sendAutoDew(value=self.ui.autoDew.isChecked())
        return suc
