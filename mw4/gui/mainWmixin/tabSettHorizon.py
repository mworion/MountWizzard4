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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import


class SettHorizon:
    """
    """

    def __init__(self):
        self.ui.saveHorizonMask.clicked.connect(self.saveHorizonMask)
        self.ui.saveHorizonMaskAs.clicked.connect(self.saveHorizonMaskAs)
        self.ui.loadHorizonMask.clicked.connect(self.loadHorizonMask)
        self.ui.clearHorizonMask.clicked.connect(self.clearHorizonMask)

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
            self.app.drawHorizonPoints.emit()

        else:
            self.app.message.emit(f'Horizon mask [{fileName}] cannot no be loaded', 2)

        self.app.redrawHemisphere.emit()

        return True

    def saveHorizonMask(self):
        """
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

    def clearHorizonMask(self):
        """
        :return:
        """
        self.app.data.horizonP = []
        self.ui.horizonFileName.setText('')
        self.app.redrawHemisphere.emit()
        return True
