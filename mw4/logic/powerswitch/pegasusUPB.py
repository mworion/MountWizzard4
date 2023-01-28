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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform

# external packages

# local imports
from base.driverDataClass import Signals
from logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi
from logic.powerswitch.pegasusUPBAscom import PegasusUPBAscom
from logic.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca


class PegasusUPB:

    __all__ = ['PegasusUPB']

    log = logging.getLogger(__name__)

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': PegasusUPBIndi(self.app, self.signals, self.data),
            'alpaca': PegasusUPBAlpaca(self.app, self.signals, self.data),
        }
        if platform.system() == 'Windows':
            self.run['ascom'] = PegasusUPBAscom(self.app, self.signals, self.data)

        for fw in self.run:
            self.defaultConfig['frameworks'].update({fw: self.run[fw].defaultConfig})

    @property
    def updateRate(self):
        return self.run[self.framework].updateRate

    @updateRate.setter
    def updateRate(self, value):
        value = int(value)
        for fw in self.run:
            self.run[fw].updateRate = value

    @property
    def loadConfig(self):
        return self.run[self.framework].loadConfig

    @loadConfig.setter
    def loadConfig(self, value):
        value = bool(value)
        for fw in self.run:
            self.run[fw].loadConfig = value

    def startCommunication(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].startCommunication()
        return suc

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].stopCommunication()
        return suc

    def togglePowerPort(self, port=None):
        """
        :param port:
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].togglePowerPort(port=port)
        return suc

    def togglePowerPortBoot(self, port=None):
        """
        :param port:
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].togglePowerPortBoot(port=port)
        return suc

    def toggleHubUSB(self):
        """
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].toggleHubUSB()
        return suc

    def togglePortUSB(self, port=None):
        """
        :param port:
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].togglePortUSB(port=port)
        return suc

    def toggleAutoDew(self):
        """
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].toggleAutoDew()
        return suc

    def sendDew(self, port='', value=None):
        """
        :param port:
        :param value:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].sendDew(port=port, value=value)
        return suc

    def sendAdjustableOutput(self, value=None):
        """
        :param value:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].sendAdjustableOutput(value=value)
        return suc

    def reboot(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].reboot()
        return suc
