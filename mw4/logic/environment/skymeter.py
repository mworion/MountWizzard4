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
import logging
import platform

# external packages

# local imports
from base.driverDataClass import Signals
from logic.environment.skymeterIndi import SkymeterIndi
from logic.environment.skymeterAlpaca import SkymeterAlpaca
if platform.system() == 'Windows':
    from logic.environment.skymeterAscom import SkymeterAscom


class Skymeter:
    """
    """

    __all__ = ['Skymeter']
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
            'indi': SkymeterIndi(self.app, self.signals, self.data),
            'alpaca': SkymeterAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == 'Windows':
            self.run['ascom'] = SkymeterAscom(self.app, self.signals, self.data)

        for fw in self.run:
            self.defaultConfig['frameworks'].update({fw: self.run[fw].defaultConfig})

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].startCommunication(loadConfig=loadConfig)
        return suc

    def stopCommunication(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].stopCommunication()
        return suc
