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
# Python  v3.6.7
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
    signalUpdateLocation = PyQt5.QtCore.pyqtSignal()

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
        self.data = build.DataPoint(lat=self.config.get('latitudeTemp', 45))
        self.data.loadHorizonP()
        self.mainW = mainW.MainWindow(self)
        self.hemisphereW = hemisphereW.HemisphereWindow(self)
        self.messageW = messageW.MessageWindow(self)

        # write basic data to message window
        self.message.emit('MountWizzard4 started', 1)
        self.message.emit('Workdir is: {0}'.format(self.mwGlob['workDir']), 1)
        self.message.emit('Profile [{0}] loaded'
                          .format(self.config.get('profileName', 'empty')), 0)

        # link cross widget gui signals
        self.mainW.ui.openMessageW.clicked.connect(self.messageW.toggleWindow)
        self.mainW.ui.openHemisphereW.clicked.connect(self.hemisphereW.toggleWindow)

        # link to update from mount signals
        self.mount.signals.settDone.connect(self.updateLocation)

        # starting cyclic polling of mount data
        self.mount.startTimers()
        self.environment.startCommunication()

    def storeConfig(self):
        """
        storeConfig collects all persistent data from mainApp and it's submodules and stores
        it in the persistence dictionary for later saving

        :return: success for test purpose
        """

        config = self.config
        config['latitudeTemp'] = self.data.lat
        self.mainW.storeConfig()
        self.messageW.storeConfig()
        self.hemisphereW.storeConfig()
        return True

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
        self.saveConfig()
        PyQt5.QtCore.QCoreApplication.quit()

    def defaultPath(self):
        return self.mwGlob['configDir'] + '/config.cfg'

    def defaultConfig(self, config=None):
        if config is None:
            config = dict()
        config['profileName'] = 'config'
        config['filePath'] = self.defaultPath()
        config['version'] = '4.0'
        return config

    def loadConfig(self, loadFilePath=None):
        """
        loadConfig loads a json file from disk and stores it to the config dicts for
        persistent data. if a file path is given, that's the relevant file, otherwise
        loadConfig loads from th default file, which is config.cfg

        :param      loadFilePath:   full path to the config file including extension
        :return:    success if file could be loaded
        """

        # looking for file existence and creating new if necessary
        if loadFilePath is None:
            loadFilePath = self.defaultPath()
        if not os.path.isfile(loadFilePath):
            self.config = self.defaultConfig()
            return True

        # parsing the default file
        try:
            with open(loadFilePath, 'r') as configFile:
                defaultData = json.load(configFile)
        except Exception as e:
            self.logger.error('Cannot parse: {0}, error: {1}'.format(loadFilePath, e))
            self.config = self.defaultConfig()
            return False

        # loading default and finishing up
        if defaultData['profileName'] == 'config':
            self.config = self.convertData(defaultData)
            self.config['filePath'] = self.defaultPath()
            return True

        # checking if reference to another file is available
        referencedFilePath = defaultData['filePath']

        # check if reference ist still to default -> correct error
        isDefault = referencedFilePath.endswith('config.cfg')
        if isDefault:
            self.config = self.convertData(defaultData)
            self.config['profileName'] = 'config'
            return True

        # now loading referenced file
        try:
            with open(referencedFilePath, 'r') as referencedFile:
                referencedData = json.load(referencedFile)
        except Exception as e:
            self.config = self.defaultConfig(defaultData)
            self.logger.error('Cannot parse: {0}, error: {1}'.format(referencedFilePath, e))
            return False

        # check if reference is in referenced file
        if 'filePath' not in referencedData:
            self.config = self.convertData(defaultData)
            self.config['filePath'] = self.defaultPath()
            self.config['profileName'] = 'config'
            self.logger.error('FilePath missing in: {0}'.format(referencedFilePath))
            return False

        # now everything should be ok
        self.config = self.convertData(referencedData)
        return True

    @staticmethod
    def convertData(data):
        """
        convertDate tries to convert data from an older or newer version of the config
        file to the actual needed one.

        :param      data:   config data as dict
        :return:    data:   config data as dict
        """

        return data

    def saveConfig(self, saveFilePath=None):
        """
        saveConfig saves a json file to disk from the config dicts for
        persistent data.

        :param      saveFilePath:   full path to the config file
        :return:    success
        """

        # default if profile is named config
        if self.config['profileName'] == 'config':
            saveFilePath = self.defaultPath()
            self.config['filePath'] = saveFilePath

        # default saving for reference
        if saveFilePath is None:
            saveFilePath = self.config.get('filePath', None)
        else:
            self.config['filePath'] = saveFilePath

        # if still no reference is there, we make it named config
        if saveFilePath is None:
            saveFilePath = self.defaultPath()
            self.config['filePath'] = saveFilePath
            self.config['profileName'] = 'config'

        # check if we have to write two data sets
        isReferenced = not saveFilePath.endswith('config.cfg')

        # save the config
        filePath = self.defaultPath()
        with open(filePath, 'w') as outfile:
            json.dump(self.config,
                      outfile,
                      sort_keys=True,
                      indent=4)
        # there is a link to another config file, so we save it too
        if isReferenced:
            with open(saveFilePath, 'w') as outfile:
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

    def updateLocation(self):
        """
        updateLocation updates the site location as soon as we have new data from the mount
        until then, the last data from the config file is used.

        :return: success
        """
        location = self.mount.obsSite.location
        if location is None:
            return False
        self.data.lat = location.latitude.degrees
        if self.config['latitudeTemp'] == location.latitude.degrees:
            return True
        self.config['latitudeTemp'] = location.latitude.degrees
        self.signalUpdateLocation.emit()
        return True
