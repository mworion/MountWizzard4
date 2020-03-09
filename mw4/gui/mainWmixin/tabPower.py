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

# external packages
import PyQt5
from PyQt5.QtWidgets import QWidget
from mountcontrol.convert import valueToInt

# local import


class Power(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self, app=None, ui=None, clickable=None, change=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable
            self.changeStyleDynamic = change

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
        self.autoDew = {'A': self.ui.autoDewA,
                        'B': self.ui.autoDewB,
                        'C': self.ui.autoDewC,
                        }
        self.current = {'1': self.ui.powerCurrent1,
                        '2': self.ui.powerCurrent2,
                        '3': self.ui.powerCurrent3,
                        '4': self.ui.powerCurrent4,
                        }
        self.label = {'1': self.ui.powerLabel1,
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
        self.clickable(self.ui.adjustableOutput).connect(self.setAdjustableOutput)

        # setting gui elements
        for name, button in self.dew.items():
            self.clickable(button).connect(self.setDew)
        for name, button in self.powerOnOFF.items():
            button.clicked.connect(self.togglePowerPort)
        for name, button in self.autoDew.items():
            button.clicked.connect(self.toggleAutoDewPort)
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

    def setGuiVersion(self, version=1):
        """
        setGuiVersion enables and disables the gui elements according to the recognized
        version the UPB.

        :param version:
        :return:
        """

        if version == 1:
            self.ui.groupAutoDew1.setVisible(True)
            self.ui.groupAutoDew2.setVisible(False)
            self.ui.groupDewC.setVisible(False)
            self.ui.groupPortUSB.setVisible(False)
            self.ui.groupAdjustableOutput.setVisible(False)

        elif version == 2:
            self.ui.groupAutoDew1.setVisible(False)
            self.ui.groupAutoDew2.setVisible(True)
            self.ui.groupDewC.setVisible(True)
            self.ui.groupPortUSB.setVisible(True)
            self.ui.groupAdjustableOutput.setVisible(True)

    def updatePowerGui(self):
        """
        updatePowerGui changes the style of the button related to the state of the Pegasus

        :return: success for test
        """

        value = self.app.power.data.get('WEATHER_PARAMETERS.WEATHER_TEMPERATURE', 0)
        self.ui.powerTemp.setText('{0:4.1f}'.format(value))
        value = self.app.power.data.get('WEATHER_PARAMETERS.WEATHER_HUMIDITY', 0)
        self.ui.powerHumidity.setText('{0:3.0f}'.format(value))
        value = self.app.power.data.get('WEATHER_PARAMETERS.WEATHER_DEWPOINT', 0)
        self.ui.powerDewPoint.setText('{0:4.1f}'.format(value))

        for name, button in self.powerOnOFF.items():
            value = self.app.power.data.get(f'POWER_CONTROL.POWER_CONTROL_{name}', False)
            self.changeStyleDynamic(button, 'running', value)

        for name, button in self.powerBoot.items():
            value = self.app.power.data.get(f'POWER_ON_BOOT.POWER_PORT_{name}', False)
            button.setChecked(value)

        for name, button in self.current.items():
            value = self.app.power.data.get(f'POWER_CURRENT.POWER_CURRENT_{name}', 0)
            button.setText(f'{value:4.2f}')

        for name, button in self.dew.items():
            value = self.app.power.data.get(f'DEW_PWM.DEW_{name}', 0)
            button.setText(f'{value:3.0f}')

        for name, button in self.label.items():
            value = self.app.power.data.get(f'POWER_CONTROL_LABEL.POWER_LABEL_{name}',
                                            f'Power {name}')
            button.setText(value)

        value = self.app.power.data.get('POWER_CONSUMPTION.CONSUMPTION_AVG_AMPS', 0)
        self.ui.consumptionAvgAmps.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('POWER_CONSUMPTION.CONSUMPTION_AMP_HOURS', 0)
        self.ui.consumptionAmpHours.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('POWER_CONSUMPTION.CONSUMPTION_WATT_HOURS', 0)
        self.ui.consumptionWattHours.setText('{0:4.2f}'.format(value))

        value = self.app.power.data.get('POWER_SENSORS.SENSOR_VOLTAGE', 0)
        self.ui.sensorVoltage.setText('{0:4.1f}'.format(value))
        value = self.app.power.data.get('POWER_SENSORS.SENSOR_CURRENT', 0)
        self.ui.sensorCurrent.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('POWER_SENSORS.SENSOR_POWER', 0)
        self.ui.sensorPower.setText('{0:4.2f}'.format(value))

        value = self.app.power.data.get('DEW_CURRENT.DEW_CURRENT_A', 0)
        self.ui.dewCurrentA.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('DEW_CURRENT.DEW_CURRENT_B', 0)
        self.ui.dewCurrentB.setText('{0:4.2f}'.format(value))
        value = self.app.power.data.get('DEW_CURRENT.DEW_CURRENT_C', 0)
        self.ui.dewCurrentC.setText('{0:4.2f}'.format(value))

        if self.app.power.data.get('VERSION.UPB', 1) == 1:
            value = self.app.power.data.get('AUTO_DEW.AUTO_DEW_ENABLED', False)
            self.changeStyleDynamic(self.ui.autoDew, 'running', value)
        else:
            value = self.app.power.data.get('AUTO_DEW.DEW_A', False)
            self.changeStyleDynamic(self.ui.autoDewA, 'running', value)
            value = self.app.power.data.get('AUTO_DEW.DEW_B', False)
            self.changeStyleDynamic(self.ui.autoDewB, 'running', value)
            value = self.app.power.data.get('AUTO_DEW.DEW_C', False)
            self.changeStyleDynamic(self.ui.autoDewC, 'running', value)

            value = self.app.power.data.get('ADJUSTABLE_VOLTAGE.ADJUSTABLE_VOLTAGE_VALUE', 0)
            self.ui.adjustableOutput.setText(f'{value:4.2f}')

            for name, button in self.portUSB.items():
                value = self.app.power.data.get(f'USB_PORT_CONTROL.PORT_{name}', False)
                self.changeStyleDynamic(button, 'running', value)

        value = self.app.power.data.get('USB_HUB_CONTROL.ENABLED', False)
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

    def toggleAutoDewPort(self):
        """
        toggleAutoDewPort  toggles the state of the power switch
        :return: success
        """

        for name, button in self.autoDew.items():
            if button != self.sender():
                continue
            suc = self.app.power.toggleAutoDewPort(port=name)
            return suc

    def setAdjustableOutput(self):
        """
        setAdjustableOutput

        :return: true fot test purpose
        """

        actValue = valueToInt(self.ui.adjustableOutput.text())

        if actValue is None:
            return False

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getDouble(self,
                                  'Set Voltage Output',
                                  'Value (0-15):',
                                  actValue,
                                  0,
                                  15,
                                  1,
                                  PyQt5.QtCore.Qt.WindowFlags(),
                                  0.1,
                                  )

        if not ok:
            return False

        suc = self.app.power.sendAdjustableOutput(value=value)
        return suc
