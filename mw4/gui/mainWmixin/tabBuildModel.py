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
# external packages
import PyQt5.QtWidgets
import PyQt5.uic
# local import


class BuildModel(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.ui.genBuildGrid.clicked.connect(self.genBuildGrid)
        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.genBuildMax.clicked.connect(self.genBuildMax)
        self.ui.genBuildMed.clicked.connect(self.genBuildMed)
        self.ui.genBuildNorm.clicked.connect(self.genBuildNorm)
        self.ui.genBuildMin.clicked.connect(self.genBuildMin)
        self.ui.genBuildFile.clicked.connect(self.genBuildFile)
        self.ui.genBuildDSO.clicked.connect(self.genBuildDSO)
        self.ui.saveBuildPoints.clicked.connect(self.saveBuildFile)
        self.ui.saveBuildPointsAs.clicked.connect(self.saveBuildFileAs)
        self.ui.loadBuildPoints.clicked.connect(self.loadBuildFile)

    def initConfig(self):
        config = self.app.config['mainW']
        self.ui.buildPFileName.setText(config.get('buildPFileName', ''))
        self.ui.numberGridPointsRow.setValue(config.get('numberGridPointsRow', 5))
        self.ui.numberGridPointsCol.setValue(config.get('numberGridPointsCol', 6))
        self.ui.altitudeMin.setValue(config.get('altitudeMin', 30))
        self.ui.altitudeMax.setValue(config.get('altitudeMax', 75))
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['buildPFileName'] = self.ui.buildPFileName.text()
        config['numberGridPointsRow'] = self.ui.numberGridPointsRow.value()
        config['numberGridPointsCol'] = self.ui.numberGridPointsCol.value()
        config['altitudeMin'] = self.ui.altitudeMin.value()
        config['altitudeMax'] = self.ui.altitudeMax.value()
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        self.wIcon(self.ui.genBuildGrid, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMax, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMed, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildNorm, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMin, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildDSO, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        return True

    def clearGUI(self):
        """
        clearGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        return True

    def genBuildGrid(self):
        """
        genBuildGrid generates a grid of point for model build based on gui data. the cols
        have to be on even numbers.

        :return: success
        """

        row = self.ui.numberGridPointsRow.value()
        col = self.ui.numberGridPointsCol.value()
        minAlt = self.ui.altitudeMin.value()
        maxAlt = self.ui.altitudeMax.value()
        suc = self.app.data.genGrid(minAlt=minAlt,
                                    maxAlt=maxAlt,
                                    numbRows=row,
                                    numbCols=col)
        if not suc:
            return False
        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildMax(self):
        """
        genBuildMax generates the point pattern based on greater circles for model build.
        the point are calculated for the observers position. max goes for approx 100 points
        effectively when removing the horizon.

        :return: success
        """

        suc = self.app.data.genGreaterCircle(selection='max')
        if not suc:
            self.app.message.emit('Build points [max] cannot be generated', 2)
            return False
        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildMed(self):
        """
        genBuildMed generates the point pattern based on greater circles for model build.
        the point are calculated for the observers position. max goes for approx 70 points
        effectively when removing the horizon.

        :return: success
        """

        suc = self.app.data.genGreaterCircle(selection='med')
        if not suc:
            self.app.message.emit('Build points [med] cannot be generated', 2)
            return False
        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildNorm(self):
        """
        genBuildNorm generates the point pattern based on greater circles for model build.
        the point are calculated for the observers position. max goes for approx 40 points
        effectively when removing the horizon.

        :return: success
        """

        suc = self.app.data.genGreaterCircle(selection='norm')
        if not suc:
            self.app.message.emit('Build points [norm] cannot be generated', 2)
            return False
        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildMin(self):
        """
        genBuildMin generates the point pattern based on greater circles for model build.
        the point are calculated for the observers position. min goes for approx 25 points
        effectively when removing the horizon.

        :return: success
        """

        suc = self.app.data.genGreaterCircle(selection='min')
        if not suc:
            self.app.message.emit('Build points [min] cannot be generated', 2)
            return False
        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildDSO(self):
        self.app.message.emit('Build points [DSO Path] is not implemented yet', 2)
        return False

    def loadBuildFile(self):
        """
        loadBuildFile calls a file selector box and selects the filename to be loaded

        :return: success
        """

        folder = self.app.mwGlob['configDir']
        loadFilePath, fileName, ext = self.openFile(self,
                                                    'Open build point file',
                                                    folder,
                                                    'Build point files (*.bpts)',
                                                    )
        if not loadFilePath:
            return False
        suc = self.app.data.loadBuildP(fileName=fileName)
        if suc:
            self.ui.buildPFileName.setText(fileName)
            self.app.message.emit('Build file [{0}] loaded'.format(fileName), 0)
        else:
            self.app.message.emit('Build file [{0}] cannot no be loaded'.format(fileName), 2)
        return True

    def saveBuildFile(self):
        """
        saveBuildFile calls saving the build file

        :return: success
        """

        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.app.message.emit('Build points file name not given', 2)
            return False
        suc = self.app.data.saveBuildP(fileName=fileName)
        if suc:
            self.app.message.emit('Build file [{0}] saved'.format(fileName), 0)
        else:
            self.app.message.emit('Build file [{0}] cannot no be saved'.format(fileName), 2)
        return True

    def saveBuildFileAs(self):
        """
        saveBuildFileAs calls a file selector box and selects the filename to be save

        :return: success
        """

        folder = self.app.mwGlob['configDir']
        saveFilePath, fileName, ext = self.saveFile(self,
                                                    'Save build point file',
                                                    folder,
                                                    'Build point files (*.bpts)',
                                                    )
        if not saveFilePath:
            return False
        suc = self.app.data.saveBuildP(fileName=fileName)
        if suc:
            self.ui.buildPFileName.setText(fileName)
            self.app.message.emit('Build file [{0}] saved'.format(fileName), 0)
        else:
            self.app.message.emit('Build file [{0}] cannot no be saved'.format(fileName), 2)
        return True

    def genBuildFile(self):
        """
        genBuildFile tries to load a give build point file and displays it for usage.

        :return: success
        """

        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.app.message.emit('Build points file name not given', 2)
            return False
        suc = self.app.data.loadBuildP(fileName=fileName)
        if not suc:
            text = 'Build points file [{0}] could not be loaded'.format(fileName)
            self.app.message.emit(text, 2)
            return False
        self.autoDeletePoints()
        return True
