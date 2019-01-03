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
import pkg_resources
# external packages
import PyQt5.QtCore
import skyfield
from mountcontrol import qtmount
# local import
from mw4.gui import mainW
from mw4.gui import messageW
from mw4.gui import hemisphereW
from mw4.relay import kmRelay
from mw4.modeldata import buildpoints
from mw4.modeldata import hipparcos
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
    version = '0.5.dev0'
    logger = logging.getLogger(__name__)

    # central message and logging dispatching
    message = PyQt5.QtCore.pyqtSignal(str, int)
    redrawHemisphere = PyQt5.QtCore.pyqtSignal()

    def __init__(self,
                 mwGlob=None,
                 ):
        super().__init__()

        # getting global app data
        self.expireData = False
        self.mwGlob = mwGlob
        pathToData = self.mwGlob['dataDir']

        # persistence management through dict
        self.config = {}
        self.loadConfig()
        expireData, topo = self.initConfig()

        # initialize commands to mount
        self.mount = qtmount.Mount(host='192.168.2.15',
                                   MAC='00.c0.08.87.35.db',
                                   pathToData=pathToData,
                                   expire=expireData,
                                   verbose=None,
                                   )

        # setting location to last know config
        self.mount.obsSite.location = topo

        # get all planets for calculation
        load = skyfield.api.Loader(pathToData,
                                   expire=expireData,
                                   verbose=None,
                                   )
        self.planets = load('de421.bsp')

        # loading other classes
        self.relay = kmRelay.KMRelay(host='192.168.2.15',
                                     )
        self.environment = environ.Environment(host='localhost')
        self.data = buildpoints.DataPoint(
                                    mwGlob=self.mwGlob,
                                    location=self.mount.obsSite.location,
                                    )
        self.hipparcos = hipparcos.Hipparcos(self,
                                             mwGlob=self.mwGlob,
                                             )
        # get the window widgets up
        self.mainW = mainW.MainWindow(self)
        self.hemisphereW = hemisphereW.HemisphereWindow(self)
        self.messageW = messageW.MessageWindow(self)

        # write basic data to message window
        self.message.emit('MountWizzard4 started', 1)
        self.message.emit('build: [{0}]'.format(self.version), 1)
        verMC = pkg_resources.get_distribution('mountcontrol').version
        self.message.emit('mountcontrol version: [{0}]'.format(verMC), 1)
        verIB = pkg_resources.get_distribution('indibase').version
        self.message.emit('indibase version: [{0}]'.format(verIB), 1)
        self.message.emit('Workdir is: [{0}]'.format(self.mwGlob['workDir']), 1)
        profile = self.config.get('profileName', '-')
        self.message.emit('Profile [{0}] loaded'.format(profile), 1)

        # link cross widget gui signals
        self.mainW.ui.openMessageW.clicked.connect(self.messageW.toggleWindow)
        self.mainW.ui.openHemisphereW.clicked.connect(self.hemisphereW.toggleWindow)

        # starting mount communication
        self.mount.startTimers()
        self.environment.startCommunication()
        self.mount.signals.mountUp.connect(self.loadMountData)

    def initConfig(self):
        """

        :return:
        """

        # check if data for skyfield expires or not and get the status for it
        if 'mainW' in self.config:
            expireData = self.config['mainW'].get('expiresYes', True)
        else:
            expireData = True
        # set observer position to last one first, to greenwich if not known
        lat = self.config.get('topoLat', 51.47)
        lon = self.config.get('topoLon', 0)
        elev = self.config.get('topoElev', 46)
        topo = skyfield.api.Topos(longitude_degrees=lon,
                                  latitude_degrees=lat,
                                  elevation_m=elev)
        return expireData, topo

    def storeConfig(self):
        """
        storeConfig collects all persistent data from mainApp and it's submodules and stores
        it in the persistence dictionary for later saving

        :return: success for test purpose
        """

        config = self.config
        location = self.mount.obsSite.location
        if location is not None:
            config['topoLat'] = location.latitude.degrees
            config['topoLon'] = location.longitude.degrees
            config['topoElev'] = location.elevation.m
        self.mainW.storeConfig()
        self.messageW.storeConfig()
        self.hemisphereW.storeConfig()
        return True

    def quit(self):
        """
        quit without saving persistence data

        :return:    True for test purpose
        """

        self.mount.stopTimers()
        PyQt5.QtCore.QCoreApplication.quit()
        return True

    def quitSave(self):
        """
        quit with saving persistence data

        :return:    True for test purpose
        """

        self.mount.stopTimers()
        self.storeConfig()
        self.saveConfig()
        PyQt5.QtCore.QCoreApplication.quit()
        return True

    @staticmethod
    def defaultConfig(config=None):
        if config is None:
            config = dict()
        config['profileName'] = 'config'
        config['version'] = '4.0'
        return config

    def loadConfig(self, name=None):
        """
        loadConfig loads a json file from disk and stores it to the config dicts for
        persistent data. if a file path is given, that's the relevant file, otherwise
        loadConfig loads from th default file, which is config.cfg

        :param      name:   name of the config file
        :return:    success if file could be loaded
        """

        configDir = self.mwGlob['configDir']
        # looking for file existence and creating new if necessary

        if name is None:
            name = 'config'
        fileName = configDir + '/' + name + '.cfg'

        if not os.path.isfile(fileName):
            self.config = self.defaultConfig()
            return True

        # parsing the default file
        try:
            with open(fileName, 'r') as configFile:
                configData = json.load(configFile)
        except Exception as e:
            self.logger.error('Cannot parse: {0}, error: {1}'.format(fileName, e))
            self.config = self.defaultConfig()
            return False

        if configData.get('profileName', '') != 'config':
            configData['profileName'] = 'config'

        # check if reference ist still to default -> correcting
        if configData.get('reference', '') == 'config':
            del configData['reference']

        # loading default and finishing up
        if configData['profileName'] == 'config':
            self.config = self.convertData(configData)
            return True

        # checking if reference to another file is available
        refName = configData['reference']

        # now loading referenced fileName
        refFileName = configDir + '/' + refName + '.cfg'
        try:
            with open(refFileName, 'r') as referencedFile:
                referencedData = json.load(referencedFile)
        except Exception as e:
            if configData.get('reference', ''):
                del configData['reference']
            self.config = self.defaultConfig(configData)
            self.logger.error('Cannot parse: {0}, error: {1}'.format(refFileName, e))
            return False

        # check if reference is in referenced file
        if 'reference' not in referencedData:
            referencedData['reference'] = refName

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

    def saveConfig(self, name=None):
        """
        saveConfig saves a json file to disk from the config dicts for
        persistent data.

        :param      name:   name of the config file
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
        :return:    status how it was called
        """
        if status:
            self.mount.workaround()
            self.mount.getFW()
            self.mount.getLocation()
            self.mount.cycleSetting()
            self.mount.getNames()
            self.mount.getAlign()
            return True
        else:
            location = self.mount.obsSite.location
            self.mount.resetData()
            self.mount.obsSite.location = location
            return False
