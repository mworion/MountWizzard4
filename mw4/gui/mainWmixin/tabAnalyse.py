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

# external packages

# local import


class Analyse(object):
    """
    """

    def __init__(self):
        self.ui.hysteresisProgress.setValue(0)
        self.ui.flexureProgress.setValue(0)
        self.app.operationRunning.emit(False)
        self.imageDirAnalyse = ''
        self.analyseName = ''

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.flexureAlt.setValue(config.get('flexureAlt', 45))
        self.ui.flexureAz.setValue(config.get('flexureAz', 45))
        self.ui.flexureDuration.setValue(config.get('flexureDuration', 60))
        self.ui.flexureTime.setValue(config.get('flexureTime', 30))
        self.ui.hysteresisMinAlt.setValue(config.get('hysteresisMinAlt', 45))
        self.ui.hysteresisRuns.setValue(config.get('hysteresisRuns', 1))
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['flexureAlt'] = self.ui.flexureAlt.value()
        config['flexureAz'] = self.ui.flexureAz.value()
        config['flexureDuration'] = self.ui.flexureDuration.value()
        config['flexureTime'] = self.ui.flexureTime.value()
        config['hysteresisMinAlt'] = self.ui.hysteresisMinAlt.value()
        config['hysteresisRuns'] = self.ui.hysteresisRuns.value()
        return True
