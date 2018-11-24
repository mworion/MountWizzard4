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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import os
import json
# external packages
import PyQt5.QtCore
from mountcontrol import qtmount
# local import
from mw4 import mainW
from mw4 import messageW
from mw4 import hemisphereW
from mw4.relay import kmRelay
from mw4.build import build
from mw4.environ import environ


class MountWizzard4(PyQt5.QtCore.QObject):
    """
    MountWizzard4 class is the main class for the application. it loads all windows and
    classes needed to fulfil the work of mountwizzard. any gui work should be handled
    through the window classes. main class is for setup, config, start, persist and
    shutdown the application.
    """

    __all__ = ['MountWizzard4',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    # central message and logging dispatching
    message = PyQt5.QtCore.pyqtSignal(str, int)

    def __init__(self,
                 mwGlob=None,
                 ):
        super().__init__()

        self.mwGlob = mwGlob

        # persistence management through dict
        self.config = {}
        self.loadConfig()

        # get timing constant
        pathToTs = self.mwGlob['configDir']
        self.mount = qtmount.Mount(host='192.168.2.15',
                                   MAC='00.c0.08.87.35.db',
                                   pathToTS=pathToTs,
                                   expire=False,
                                   verbose=False,
                                   )
        self.relay = kmRelay.KMRelay(host='192.168.2.15',
                                     )
        self.environment = environ.Environment(host='localhost')
        # managing data
        self.mount.signals.mountUp.connect(self.loadMountData)

        # get the window widgets up
        self.data = build.DataPoint()
        self.mainW = mainW.MainWindow(self)
        self.hemisphereW = hemisphereW.HemisphereWindow(self)
        self.messageW = messageW.MessageWindow(self)

        # write basic data to message window
        self.message.emit('MountWizzard4 started', 1)
        self.message.emit('Workdir is: {0}'.format(self.mwGlob['workDir']), 1)
        self.message.emit('Profile [{0}] loaded'.format(self.config['profileName']), 0)

        # link cross widget gui signals
        self.mainW.ui.openMessageW.clicked.connect(self.messageW.toggleWindow)
        self.mainW.ui.openHemisphereW.clicked.connect(self.hemisphereW.toggleWindow)

        # starting cyclic polling of mount data
        self.mount.startTimers()
        self.environment.startCommunication()

    def quit(self):
        """
        quit without saving persistence data

        :return:    nothing
        """

        self.mount.stopTimers()
        PyQt5.QtCore.QCoreApplication.quit()

    def quitSave(self):
        """
        quit with saving persistence data

        :return:    nothing
        """

        self.mount.stopTimers()
        self.mainW.storeConfig()
        self.messageW.storeConfig()
        self.hemisphereW.storeConfig()
        self.saveConfig()
        PyQt5.QtCore.QCoreApplication.quit()

    def defaultPath(self):
        return self.mwGlob['configDir'] + '/config.cfg'

    def defaultConfig(self, config={}):
        config['profileName'] = 'config'
        config['filePath'] = self.defaultPath()
        config['version'] = '4.0'
        return config

    def loadConfig(self, configFilePath=None):
        """
        loadConfig loads a json file from disk and stores it to the config dicts for
        persistent data. if a file path is given, that's the relevant file, otherwise
        loadConfig loads from th default file, which is config.cfg

        :param      configFilePath:   full path to the config file including extension
        :return:    success if file could be loaded
        """

        if configFilePath is None:
            configFilePath = self.defaultPath()
        if not os.path.isfile(configFilePath):
            self.config = self.defaultConfig()
            return True

        try:
            with open(configFilePath, 'r') as configFile:
                defaultData = json.load(configFile)
        except Exception as e:
            self.logger.error('Cannot parse: {0}, error: {1}'.format(configFile, e))
            self.config = self.defaultConfig()
            return False

        referenceFilePath = defaultData.get('filePath', None)
        if referenceFilePath is None:
            self.config = self.defaultConfig()
            return False

        isDefaultConfigPath = referenceFilePath.endswith('config.cfg')
        isReferenceName = (defaultData['profileName'] == 'config')
        if isReferenceName and not isDefaultConfigPath:
            self.config = self.defaultConfig()
            return False
        try:
            with open(referenceFilePath, 'r') as referenceFile:
                referenceData = json.load(referenceFile)
        except Exception as e:
            self.config = self.defaultConfig(defaultData)
            self.logger.error('Cannot parse: {0}, error: {1}'.format(referenceFilePath, e))
            return False

        # check compatibility
        if 'version' not in referenceData:
            # data is missing, we use the standard config data
            self.config = self.defaultConfig()
            return False

        self.config = self.convertData(referenceData)
        return True

    def convertData(self, data):
        """
        convertDate tries to convert data from an older or newer version of the config
        file to the actual needed one.

        :param      data:   config data as dict
        :return:    data:   config data as dict
        """

        return data

    def saveConfig(self, referenceFilePath=None):
        """
        saveConfig saves a json file to disk from the config dicts for
        persistent data.

        :param      referenceFilePath:   full path to the config file
        :return:    success
        """

        # check necessary data available
        defaultFilePath = self.config.get('filePath', '')
        isDefaultConfigPath = defaultFilePath.endswith('config.cfg')
        isReferenceName = (self.config['profileName'] == 'config')
        if isReferenceName and not isDefaultConfigPath:
            return False

        if referenceFilePath is None:
            referenceFilePath = self.config.get('filePath', None)
        self.config['filePath'] = referenceFilePath

        # save the config
        defaultFilePath = self.defaultPath()
        with open(defaultFilePath, 'w') as outfile:
            json.dump(self.config,
                      outfile,
                      sort_keys=True,
                      indent=4)
        # there is a link to another config file, so we save it too
        if referenceFilePath is None:
            return False
        with open(referenceFilePath, 'w') as outfile:
            # make the file human readable
            json.dump(self.config,
                      outfile,
                      sort_keys=True,
                      indent=4)
        return True

    def loadMountData(self, status):
        """
        loadMountData polls data from mount if connected otherwise clears all entries
        in attributes.

        :param      status: connection status to mount computer
        :return:    True if success for test
        """
        if status:
            self.mount.workaround()
            self.mount.getFW()
            self.mount.getLocation()
            self.mount.cycleSetting()
            self.mount.getNames()
            self.mount.getAlign()
        else:
            self.mount.resetData()
        return True
