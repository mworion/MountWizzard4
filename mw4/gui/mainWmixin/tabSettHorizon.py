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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
# local import


class SettHorizon(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

        self.ui.saveHorizonMask.clicked.connect(self.saveHorizonMask)
        self.ui.saveHorizonMaskAs.clicked.connect(self.saveHorizonMaskAs)
        self.ui.loadHorizonMask.clicked.connect(self.loadHorizonMask)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.horizonFileName.setText(config.get('horizonFileName', ''))
        fileName = self.app.config['mainW'].get('horizonFileName')
        self.app.data.loadHorizonP(fileName=fileName)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['horizonFileName'] = self.ui.horizonFileName.text()

        return True

    def loadHorizonMask(self):
        """
        loadHorizonMask calls a file selector box and selects the filename to be loaded

        :return: success
        """

        folder = self.app.mwGlob['configDir']
        fileTypes = 'Horizon mask files (*.hpts);; CSV Files (*.csv);; MW3 Files (*.txt)'
        loadFilePath, fileName, ext = self.openFile(self,
                                                    'Open horizon mask file',
                                                    folder,
                                                    fileTypes)
        if not loadFilePath:
            return False

        suc = self.app.data.loadHorizonP(fileName=fileName, ext=ext)

        if suc:
            self.ui.horizonFileName.setText(fileName)
            self.app.message.emit(f'Horizon mask [{fileName}] loaded', 0)
            self.app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
        else:
            self.app.message.emit(f'Horizon mask [{fileName}] cannot no be loaded', 2)

        self.app.redrawHemisphere.emit()

        return True

    def saveHorizonMask(self):
        """
        saveHorizonMask calls saving the build file

        :return: success
        """

        fileName = self.ui.horizonFileName.text()
        if not fileName:
            self.app.message.emit('Horizon mask file name not given', 2)
            return False
        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.app.message.emit(f'Horizon mask [{fileName}] saved', 0)
        else:
            self.app.message.emit(f'Horizon mask [{fileName}] cannot no be saved', 2)
        return True

    def saveHorizonMaskAs(self):
        """
        saveHorizonMaskAs calls a file selector box and selects the filename to be save

        :return: success
        """

        folder = self.app.mwGlob['configDir']
        saveFilePath, fileName, ext = self.saveFile(self,
                                                    'Save horizon mask file',
                                                    folder,
                                                    'Horizon mask files (*.hpts)',
                                                    )
        if not saveFilePath:
            return False
        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.ui.horizonFileName.setText(fileName)
            self.app.message.emit(f'Horizon mask [{fileName}] saved', 0)
        else:
            self.app.message.emit(f'Horizon mask [{fileName}] cannot no be saved', 2)
        return True
