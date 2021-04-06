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
import PyQt5
from mountcontrol.convert import valueToInt

# local import


class Power(object):
    """
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
        self.dewLabel = {1: self.ui.groupDewA,
                         2: self.ui.groupDewB,
                         3: self.ui.groupDewC,
                         }
        self.current = {'1': self.ui.powerCurrent1,
                        '2': self.ui.powerCurrent2,
                        '3': self.ui.powerCurrent3,
                        '4': self.ui.powerCurrent4,
                        }
        self.powerLabel = {'1': self.ui.powerLabel1,
                           '2': self.ui.powerLabel2,
                           '3': self.ui.powerLabel3,
                           '4': self.ui.powerLabel4,
                           }
        self.portUSB = {'1': self.ui.portUSB1,
                        '2': self.ui.portUSB2,
                        '3': self.ui.portUSB3,
                        '4': self.ui.portUSB4,
                        '5': self.ui.portUSB5,
                        '6': self.ui.portUSB6,
                        }

        # gui tasks
        self.ui.hubUSB.clicked.connect(self.toggleHubUSB)
        self.ui.autoDew.clicked.connect(self.toggleAutoDew)
        self.ui.rebootUPB.clicked.connect(self.rebootUPB)
        self.clickable(self.ui.adjustableOutput).connect(self.setAdjustableOutput)

        # setting gui elements
        for name, button in self.dew.items():
            self.clickable(button).connect(self.setDew)
        for name, button in self.powerOnOFF.items():
            button.clicked.connect(self.togglePowerPort)
        for name, button in self.powerBoot.items():
            button.clicked.connect(self.togglePowerBootPort)
        for name, button in self.portUSB.items():
            button.clicked.connect(self.togglePortUSB)

        # functional signals
        self.app.power.signals.version.connect(self.setGuiVersion)

        # cyclic tasks
        self.app.update1s.connect(self.updatePowerGui)

    def clearPowerGui(self):
        """
        clearPowerGui changes the state of the Pegasus values to '-'

        :return: success for test
        """
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

    def setGuiVersion(self, version=1):
        """
        setGuiVersion enables and disables the gui elements according to the recognized
        version the UPB.

        :param version:
        :return:
        """
        if version == 1:
            self.ui.groupDewC.setVisible(False)
            self.ui.groupPortUSB.setVisible(False)
            self.ui.groupHubUSB.setVisible(True)
            self.ui.groupAdjustableOutput.setVisible(False)
        elif version == 2:
            self.ui.groupDewC.setVisible(True)
            self.ui.groupPortUSB.setVisible(True)
            self.ui.groupHubUSB.setVisible(False)
            self.ui.groupAdjustableOutput.setVisible(True)

    def updatePowerGui(self):
        """
        updatePowerGui changes the style of the button related to the state of the Pegasus

        :return: success for test
        """
        for name, button in self.powerOnOFF.items():
            value = self.app.power.data.get(f'POWER_CONTROL.POWER_CONTROL_{name}', False)
            self.changeStyleDynamic(button, 'running', value)

        for name, button in self.powerBoot.items():
            value = self.app.power.data.get(f'POWER_ON_BOOT.POWER_PORT_{name}', False)
            button.setChecked(value)

        for name, button in self.current.items():
            value = self.app.power.data.get(f'POWER_CURRENT.POWER_CURRENT_{name}')
            self.guiSetText(button, '4.2f', value)

        for name, button in self.dew.items():
            value = self.app.power.data.get(f'DEW_PWM.DEW_{name}')
            self.guiSetText(button, '3.0f', value)

        for name, button in self.dewLabel.items():
            value = self.app.power.data.get(f'DEW_CONTROL_LABEL.DEW_LABEL_{name}', '')
            button.setTitle(f'{value:1s}')

        for name, button in self.powerLabel.items():
            value = self.app.power.data.get(f'POWER_CONTROL_LABEL.POWER_LABEL_{name}',
                                            f'Power {name}')
            button.setText(value)

        value = self.app.power.data.get('POWER_CONSUMPTION.CONSUMPTION_AVG_AMPS')
        self.guiSetText(self.ui.consumptionAvgAmps, '4.2f', value)
        value = self.app.power.data.get('POWER_CONSUMPTION.CONSUMPTION_AMP_HOURS')
        self.guiSetText(self.ui.consumptionAmpHours, '4.2f', value)
        value = self.app.power.data.get('POWER_CONSUMPTION.CONSUMPTION_WATT_HOURS')
        self.guiSetText(self.ui.consumptionWattHours, '4.2f', value)

        value = self.app.power.data.get('POWER_SENSORS.SENSOR_VOLTAGE')
        self.guiSetText(self.ui.sensorVoltage, '4.1f', value)
        value = self.app.power.data.get('POWER_SENSORS.SENSOR_CURRENT')
        self.guiSetText(self.ui.sensorCurrent, '4.2f', value)
        value = self.app.power.data.get('POWER_SENSORS.SENSOR_POWER')
        self.guiSetText(self.ui.sensorPower, '4.2f', value)

        value = self.app.power.data.get('DEW_CURRENT.DEW_CURRENT_A')
        self.guiSetText(self.ui.dewCurrentA, '4.2f', value)
        value = self.app.power.data.get('DEW_CURRENT.DEW_CURRENT_B')
        self.guiSetText(self.ui.dewCurrentB, '4.2f', value)
        value = self.app.power.data.get('DEW_CURRENT.DEW_CURRENT_C')
        self.guiSetText(self.ui.dewCurrentC, '4.2f', value)

        value1 = self.app.power.data.get('AUTO_DEW.INDI_ENABLED', False)
        value2 = self.app.power.data.get('AUTO_DEW.DEW_A', False)
        value3 = self.app.power.data.get('AUTO_DEW.DEW_B', False)
        value4 = self.app.power.data.get('AUTO_DEW.DEW_C', False)
        value = value1 or value2 or value3 or value4
        self.changeStyleDynamic(self.ui.autoDew, 'running', value)

        if self.app.power.data.get('FIRMWARE_INFO.VERSION', '1.4') > '1.4':
            value = self.app.power.data.get('ADJUSTABLE_VOLTAGE.ADJUSTABLE_VOLTAGE_VALUE')
            self.guiSetText(self.ui.adjustableOutput, '4.1f', value)

            for name, button in self.portUSB.items():
                value = self.app.power.data.get(f'USB_PORT_CONTROL.PORT_{name}', False)
                self.changeStyleDynamic(button, 'running', value)

        else:
            value = self.app.power.data.get('USB_HUB_CONTROL.INDI_ENABLED', False)
            self.changeStyleDynamic(self.ui.hubUSB, 'running', value)

        return True

    def setDew(self):
        """
        setDew send the new dew value to power. as self.sender() gives only the object
        back, which is in case of an QLineEdit a wrapper, we have to go to the parent
        object to get the line edit object directly

        :return: true fot test purpose
        """

        for name, button in self.dew.items():
            if button != self.sender().parent():
                continue

            actValue = valueToInt(button.text())

            if actValue is None:
                return False

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
            suc = self.app.power.togglePowerPort(port=name)
            return suc

    def togglePowerBootPort(self):
        """
        togglePowerPort  toggles the state of the power switch
        :return: success
        """

        for name, button in self.powerBoot.items():
            if button != self.sender():
                continue
            suc = self.app.power.togglePowerPortBoot(port=name)
            return suc

    def toggleHubUSB(self):
        """
        toggleHubUSB

        :return: true fot test purpose
        """
        suc = self.app.power.toggleHubUSB()
        return suc

    def togglePortUSB(self):
        """
        toggleUSBPort  toggles the state of the power switch
        :return: success
        """

        for name, button in self.portUSB.items():
            if button != self.sender():
                continue
            suc = self.app.power.togglePortUSB(port=name)
            return suc

    def toggleAutoDew(self):
        """
        toggleAutoDew

        :return: true fot test purpose
        """

        suc = self.app.power.toggleAutoDew()
        return suc

    def setAdjustableOutput(self):
        """
        setAdjustableOutput

        :return: true fot test purpose
        """

        actValue = float(self.ui.adjustableOutput.text())

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getDouble(self,
                                  'Set Voltage Output',
                                  'Value (3-12):',
                                  actValue,
                                  3,
                                  12,
                                  1,
                                  PyQt5.QtCore.Qt.WindowFlags(),
                                  0.1,
                                  )

        if not ok:
            return False

        suc = self.app.power.sendAdjustableOutput(value=value)
        return suc

    def rebootUPB(self):
        """

        :return: true fot test purpose
        """

        suc = self.app.power.reboot()
        return suc
