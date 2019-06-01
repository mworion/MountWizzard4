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
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import


class AlignMount(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        ms = self.app.mount.signals
        ms.alignDone.connect(self.updateAlignGUI)
        ms.alignDone.connect(self.updateTurnKnobsGUI)

        self.ui.genAlignBuild.clicked.connect(self.genAlignBuild)
        self.ui.genAlignBuildFile.clicked.connect(self.genAlignBuildFile)
        self.ui.altBase.valueChanged.connect(self.genAlignBuild)
        self.ui.azBase.valueChanged.connect(self.genAlignBuild)
        self.ui.numberBase.valueChanged.connect(self.genAlignBuild)
        self.ui.saveAlignBuildPoints.clicked.connect(self.saveAlignBuildFile)
        self.ui.saveAlignBuildPointsAs.clicked.connect(self.saveAlignBuildFileAs)
        self.ui.loadAlignBuildPoints.clicked.connect(self.loadAlignBuildFile)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.alignBuildPFileName.setText(config.get('alignBuildPFileName', ''))

        self.ui.altBase.valueChanged.disconnect(self.genAlignBuild)
        self.ui.azBase.valueChanged.disconnect(self.genAlignBuild)
        self.ui.numberBase.valueChanged.disconnect(self.genAlignBuild)

        self.ui.altBase.setValue(config.get('altBase', 30))
        self.ui.azBase.setValue(config.get('azBase', 45))
        self.ui.numberBase.setValue(config.get('numberBase', 3))

        # initialising the signal slot connections after the value are set, because
        # otherwise we get a first value changed signal just when populating
        # the initial data. this should not happen.
        self.ui.altBase.valueChanged.connect(self.genAlignBuild)
        self.ui.azBase.valueChanged.connect(self.genAlignBuild)
        self.ui.numberBase.valueChanged.connect(self.genAlignBuild)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['alignBuildPFileName'] = self.ui.alignBuildPFileName.text()
        config['altBase'] = self.ui.altBase.value()
        config['azBase'] = self.ui.azBase.value()
        config['numberBase'] = self.ui.numberBase.value()
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """

        self.wIcon(self.ui.genAlignBuild, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.plateSolveSync, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        pixmap = PyQt5.QtGui.QPixmap(':/azimuth1.png')
        self.ui.picAZ.setPixmap(pixmap)
        pixmap = PyQt5.QtGui.QPixmap(':/altitude1.png')
        self.ui.picALT.setPixmap(pixmap)
        return True

    def updateAlignGUI(self, model):
        """
        updateAlignGUI shows the data which is received through the getain command. this is
        mainly polar and ortho errors as well as basic model data.

        :param model:
        :return:    True if ok for testing
        """

        if model.numberStars is not None:
            text = str(model.numberStars)
        else:
            text = '-'
        self.ui.numberStars.setText(text)
        self.ui.numberStars1.setText(text)

        if model.terms is not None:
            text = str(model.terms)
        else:
            text = '-'
        self.ui.terms.setText(text)

        if model.errorRMS is not None:
            text = str(model.errorRMS)
        else:
            text = '-'
        self.ui.errorRMS.setText(text)
        self.ui.errorRMS1.setText(text)

        if model.positionAngle is not None:
            text = f'{model.positionAngle.degrees:5.1f}'
        else:
            text = '-'
        self.ui.positionAngle.setText(text)

        if model.polarError is not None:
            text = f'{model.polarError.degrees * 60:5.2f}'
        else:
            text = '-'
        self.ui.polarError.setText(text)

        if model.orthoError is not None:
            text = f'{model.orthoError.degrees * 60:5.2f}'
        else:
            text = '-'
        self.ui.orthoError.setText(text)

        if model.azimuthError is not None:
            text = f'{model.azimuthError.degrees:5.1f}'
        else:
            text = '-'
        self.ui.azimuthError.setText(text)

        if model.altitudeError is not None:
            text = f'{model.altitudeError.degrees:5.1f}'
        else:
            text = '-'
        self.ui.altitudeError.setText(text)

        return True

    def updateTurnKnobsGUI(self, model):
        """
        updateTurnKnobsGUI shows the data which is received through the getain command.
        this is mainly polar and ortho errors as well as basic model data.

        :param model:
        :return:    True if ok for testing
        """

        if model.azimuthTurns is not None:
            if model.azimuthTurns > 0:
                text = '{0:3.1f} revs left'.format(abs(model.azimuthTurns))
            else:
                text = '{0:3.1f} revs right'.format(abs(model.azimuthTurns))
        else:
            text = '-'
        self.ui.azimuthTurns.setText(text)

        if model.altitudeTurns is not None:
            if model.altitudeTurns > 0:
                text = '{0:3.1f} revs down'.format(abs(model.altitudeTurns))
            else:
                text = '{0:3.1f} revs up'.format(abs(model.altitudeTurns))
        else:
            text = '-'
        self.ui.altitudeTurns.setText(text)

        return True

    def genAlignBuild(self):
        """
        genAlignBuild generates a grid of point for model build based on gui data. the cols
        have to be on even numbers.

        :return: success
        """

        self.lastModelType = 'align-grid'
        altBase = self.ui.altBase.value()
        azBase = self.ui.azBase.value()
        numberBase = self.ui.numberBase.value()
        suc = self.app.data.genAlign(altBase=altBase,
                                     azBase=azBase,
                                     numberBase=numberBase,
                                     )
        if not suc:
            return False
        self.autoDeletePoints()
        return True

    def loadAlignBuildFile(self):
        """
        loadAlignBuildFile calls a file selector box and selects the filename to be loaded

        :return: success
        """

        folder = self.app.mwGlob['configDir']
        loadFilePath, fileName, ext = self.openFile(self,
                                                    'Open align build point file',
                                                    folder,
                                                    'Build point files (*.bpts)',
                                                    )
        if not loadFilePath:
            return False
        suc = self.app.data.loadBuildP(fileName=fileName)
        if suc:
            self.ui.alignBuildPFileName.setText(fileName)
            self.app.message.emit('Align build file [{0}] loaded'.format(fileName), 0)
        else:
            self.app.message.emit('Align build file [{0}] cannot no be loaded'
                                  .format(fileName), 2)
        return True

    def saveAlignBuildFile(self):
        """
        saveAlignBuildFile calls saving the build file

        :return: success
        """

        fileName = self.ui.alignBuildPFileName.text()
        if not fileName:
            self.app.message.emit('Align build points file name not given', 2)
            return False
        suc = self.app.data.saveBuildP(fileName=fileName)
        if suc:
            self.app.message.emit('Align build file [{0}] saved'.format(fileName), 0)
        else:
            self.app.message.emit('Align build file [{0}] cannot no be saved'
                                  .format(fileName), 2)
        return True

    def saveAlignBuildFileAs(self):
        """
        saveAlignBuildFileAs calls a file selector box and selects the filename to be save

        :return: success
        """

        folder = self.app.mwGlob['configDir']
        saveFilePath, fileName, ext = self.saveFile(self,
                                                    'Save align build point file',
                                                    folder,
                                                    'Build point files (*.bpts)',
                                                    )
        if not saveFilePath:
            return False
        suc = self.app.data.saveBuildP(fileName=fileName)
        if suc:
            self.ui.alignBuildPFileName.setText(fileName)
            self.app.message.emit('Align build file [{0}] saved'.format(fileName), 0)
        else:
            self.app.message.emit('Align build file [{0}] cannot no be saved'
                                  .format(fileName), 2)
        return True

    def genAlignBuildFile(self):
        """
        genAlignBuildFile tries to load a give build point file and displays it for usage.

        :return: success
        """

        fileName = self.ui.alignBuildPFileName.text()
        if not fileName:
            self.app.message.emit('Align build points file name not given', 2)
            return False

        self.lastModelType = 'align-file'
        suc = self.app.data.loadBuildP(fileName=fileName)
        if not suc:
            text = 'Align build points file [{0}] could not be loaded'.format(fileName)
            self.app.message.emit(text, 2)
            return False
        self.autoDeletePoints()
        return True
