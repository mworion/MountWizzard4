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
from logic.cover.coverIndi import CoverIndi
from logic.cover.coverAlpaca import CoverAlpaca
if platform.system() == 'Windows':
    from logic.cover.coverAscom import CoverAscom


class Cover:

    __all__ = ['Cover']
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
            'indi': CoverIndi(self.app, self.signals, self.data),
            'alpaca': CoverAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == 'Windows':
            self.run['ascom'] = CoverAscom(self.app, self.signals, self.data)

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
        :return:
        """
        if self.framework not in self.run.keys():
            return False
        suc = self.run[self.framework].startCommunication()
        return suc

    def stopCommunication(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].stopCommunication()
        return suc

    def closeCover(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].closeCover()
        return suc

    def openCover(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].openCover()
        return suc

    def haltCover(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].haltCover()
        return suc

    def lightOn(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].lightOn()
        return suc

    def lightOff(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].lightOff()
        return suc

    def lightIntensity(self, value):
        """
        :param value:
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].lightIntensity(value)
        return suc
