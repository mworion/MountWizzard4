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
# local import
import mountwizzard4.mw4_global
import mountcontrol.qtmount
import mountwizzard4.gui.mainW
import mountwizzard4.gui.messageW


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

    def __init__(self):
        super().__init__()

        # persistence management through dict
        self.config = {}
        self.loadConfig()

        # get the working horses up
        pathToTs = mountwizzard4.mw4_global.work_dir + '/config'
        self.mount = mountcontrol.qtmount.Mount(host='192.168.2.15',
                                                MAC='00.c0.08.87.35.db',
                                                pathToTS=pathToTs,
                                                expire=False,
                                                verbose=False,
                                                )
        # managing data
        self.mount.signals.mountUp.connect(self.loadMountData)

        # get the window widgets up
        self.mainW = mountwizzard4.gui.mainW.MainWindow(self)
        self.messageW = mountwizzard4.gui.messageW.MessageWindow(self)

        # link cross widget gui signals
        self.mainW.ui.openMessageW.clicked.connect(self.messageW.toggleWindow)

        # starting cyclic polling of mount data
        self.mount.startTimers()

        # write basic data to message window
        self.message.emit('MountWizzard4 started', 1)
        self.message.emit('Workdir is: {0}'.format(mountwizzard4.mw4_global.work_dir), 1)

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
        self.saveConfig()
        PyQt5.QtCore.QCoreApplication.quit()

    def loadConfig(self, filePath=None):
        """
        loadConfig loads a json file from disk and stores it to the config dicts for
        persistent data.

        :param      filePath:   full path to the config file
        :return:    success
        """

        if filePath is None:
            filePath = mountwizzard4.mw4_global.config_dir + '/config.cfg'
        self.config = {'name': 'config'}
        if not os.path.isfile(filePath):
            return False
        try:
            with open(filePath, 'r') as data_file:
                loadData = json.load(data_file)
        except Exception as e:
            self.logger.error('Cannot parse: {0}, error: {1}'.format(filePath, e))
            return False
        if 'filePath' not in loadData:
            self.logger.error('Cannot load, because no file path in config.cfg')
            return False
        # now we have the true file path
        filePath = loadData['filePath']
        if filePath is not None:
            if not os.path.isfile(filePath):
                return False
            try:
                with open(filePath, 'r') as data_file:
                    loadData = json.load(data_file)
            except Exception as e:
                self.logger.error('Cannot parse: {0}, error: {1}'.format(filePath, e))
                return False
        if 'version' not in loadData:
            return False
        if loadData['version'] != '4.0':
            loadData = self.convertData(loadData)
        self.config = loadData
        return True

    def saveConfig(self, filePath=None, name=None):
        """
        saveConfig saves a json file to disk from the config dicts for
        persistent data.

        :param      filePath:   full path to the config file
        :param      name:       name of the configuration
        :return:    success
        """

        self.config['version'] = '4.0'
        self.config['filePath'] = filePath
        self.config['name'] = name
        configPath = mountwizzard4.mw4_global.config_dir + '/config.cfg'
        if filePath is not None:
            with open(filePath, 'w') as outfile:
                # make the file human readable
                json.dump(self.config,
                          outfile,
                          sort_keys=True,
                          indent=4)
        if name is None:
            self.config['name'] = 'config'
        with open(configPath, 'w') as outfile:
            json.dump(self.config,
                      outfile,
                      sort_keys=True,
                      indent=4)
        return True

    def convertData(self, data):
        """
        convertDate tries to convert data from an older or newer version of the config
        file to the actual needed one.

        :param      data:   config data as dict
        :return:    data:   config data as dict
        """

        return data

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
