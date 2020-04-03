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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import


class BuildPoints(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.

    as the mainW class is very big i have chosen to use mixins to extend the readability
    of the code and extend the mainW class by additional parent classes.

    BuildPoints handles all topics around generating the build point and horizon settings
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable
        # persistence for the type of generator used
        self.lastGenerator = 'none'

        # gui interaction signals
        self.ui.genBuildGrid.clicked.connect(self.genBuildGrid)
        self.ui.genBuildAlign3.clicked.connect(self.genBuildAlign3)
        self.ui.genBuildAlign6.clicked.connect(self.genBuildAlign6)
        self.ui.genBuildAlign9.clicked.connect(self.genBuildAlign9)
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
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.durationDSO.valueChanged.connect(self.genBuildDSO)
        self.ui.timeShiftDSO.valueChanged.connect(self.genBuildDSO)
        self.ui.saveBuildPoints.clicked.connect(self.saveBuildFile)
        self.ui.saveBuildPointsAs.clicked.connect(self.saveBuildFileAs)
        self.ui.loadBuildPoints.clicked.connect(self.loadBuildFile)
        self.ui.genBuildSpiralMax.clicked.connect(self.genBuildSpiralMax)
        self.ui.genBuildSpiralMed.clicked.connect(self.genBuildSpiralMed)
        self.ui.genBuildSpiralNorm.clicked.connect(self.genBuildSpiralNorm)
        self.ui.genBuildSpiralMin.clicked.connect(self.genBuildSpiralMin)
        self.ui.clearBuildP.clicked.connect(self.clearBuildP)
        self.ui.checkSortNothing.clicked.connect(self.updateSorting)
        self.ui.checkSortEW.clicked.connect(self.updateSorting)
        self.ui.checkSortHL.clicked.connect(self.updateSorting)
        self.ui.checkAutoDeleteMeridian.clicked.connect(self.autoDeletePoints)
        self.ui.checkAutoDeleteHorizon.clicked.connect(self.autoDeletePoints)


    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']

        self.ui.numberGridPointsCol.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.disconnect(self.genBuildDSO)
        self.ui.durationDSO.valueChanged.disconnect(self.genBuildDSO)
        self.ui.timeShiftDSO.valueChanged.disconnect(self.genBuildDSO)

        self.ui.buildPFileName.setText(config.get('buildPFileName', ''))
        self.ui.numberGridPointsRow.setValue(config.get('numberGridPointsRow', 5))
        self.ui.numberGridPointsCol.setValue(config.get('numberGridPointsCol', 6))
        self.ui.altitudeMin.setValue(config.get('altitudeMin', 30))
        self.ui.altitudeMax.setValue(config.get('altitudeMax', 75))
        self.ui.numberDSOPoints.setValue(config.get('numberDSOPoints', 20))
        self.ui.durationDSO.setValue(config.get('durationDSO', 5))
        self.ui.timeShiftDSO.setValue(config.get('timeShiftDSO', 0))

        # initialising the signal slot connections after the value are set, because
        # otherwise we get a first value changed signal just when populating
        # the initial data. this should not happen.
        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.durationDSO.valueChanged.connect(self.genBuildDSO)
        self.ui.timeShiftDSO.valueChanged.connect(self.genBuildDSO)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        config['buildPFileName'] = self.ui.buildPFileName.text()
        config['numberGridPointsRow'] = self.ui.numberGridPointsRow.value()
        config['numberGridPointsCol'] = self.ui.numberGridPointsCol.value()
        config['altitudeMin'] = self.ui.altitudeMin.value()
        config['altitudeMax'] = self.ui.altitudeMax.value()
        config['numberDSOPoints'] = self.ui.numberDSOPoints.value()
        config['durationDSO'] = self.ui.durationDSO.value()
        config['timeShiftDSO'] = self.ui.timeShiftDSO.value()

        return True

    def genBuildGrid(self):
        """
        genBuildGrid generates a grid of point for model build based on gui data. the cols
        have to be on even numbers.

        :return: success
        """

        self.lastGenerator = 'grid'

        self.ui.numberGridPointsRow.setEnabled(False)
        self.ui.numberGridPointsCol.setEnabled(False)
        self.ui.altitudeMin.setEnabled(False)
        self.ui.altitudeMax.setEnabled(False)

        row = self.ui.numberGridPointsRow.value()
        col = self.ui.numberGridPointsCol.value()

        # we only have equal cols
        col = 2 * int(col / 2)
        self.ui.numberGridPointsCol.setValue(col)
        minAlt = self.ui.altitudeMin.value()
        maxAlt = self.ui.altitudeMax.value()
        suc = self.app.data.genGrid(minAlt=minAlt,
                                    maxAlt=maxAlt,
                                    numbRows=row,
                                    numbCols=col)
        if not suc:
            self.ui.numberGridPointsRow.setEnabled(True)
            self.ui.numberGridPointsCol.setEnabled(True)
            self.ui.altitudeMin.setEnabled(True)
            self.ui.altitudeMax.setEnabled(True)
            self.app.message.emit('Could not generate grid', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        self.ui.numberGridPointsRow.setEnabled(True)
        self.ui.numberGridPointsCol.setEnabled(True)
        self.ui.altitudeMin.setEnabled(True)
        self.ui.altitudeMax.setEnabled(True)

        return True

    def genBuildAlign3(self):
        """
        genBuildAlign3 generates a grid of 3 point for model build based on gui data.

        :return: success
        """

        self.lastGenerator = 'align3'
        suc = self.app.data.genAlign(altBase=55,
                                     azBase=10,
                                     numberBase=3)
        if not suc:
            self.app.message.emit('Could not generate 3 align stars', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildAlign6(self):
        """
        genBuildAlign6 generates a grid of 6 point for model build based on gui data.

        :return: success
        """

        self.lastGenerator = 'align6'
        suc = self.app.data.genAlign(altBase=55,
                                     azBase=10,
                                     numberBase=6)
        if not suc:
            self.app.message.emit('Could not generate 6 align stars', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildAlign9(self):
        """
        genBuildAlign9 generates a grid of 9 point for model build based on gui data.

        :return: success
        """

        self.lastGenerator = 'align9'
        suc = self.app.data.genAlign(altBase=55,
                                     azBase=10,
                                     numberBase=9)
        if not suc:
            self.app.message.emit('Could not generate 9 align stars', 2)
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

        self.lastGenerator = 'max'
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

        self.lastGenerator = 'med'
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

        self.lastGenerator = 'norm'
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

        self.lastGenerator = 'min'
        suc = self.app.data.genGreaterCircle(selection='min')
        if not suc:
            self.app.message.emit('Build points [min] cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildDSO(self):
        """
        genBuildDSO generates points along the actual tracking path

        :return: success
        """

        self.lastGenerator = 'dso'
        ra = self.app.mount.obsSite.raJNow
        dec = self.app.mount.obsSite.decJNow
        timeJD = self.app.mount.obsSite.timeJD
        location = self.app.mount.obsSite.location

        if ra is None or dec is None or location is None:
            self.app.message.emit('DSO Path cannot be generated', 2)
            return False

        self.ui.numberDSOPoints.setEnabled(False)
        self.ui.durationDSO.setEnabled(False)
        self.ui.timeShiftDSO.setEnabled(False)

        numberPoints = self.ui.numberDSOPoints.value()
        duration = self.ui.durationDSO.value()
        timeShift = self.ui.timeShiftDSO.value()

        suc = self.app.data.generateDSOPath(ra=ra,
                                            dec=dec,
                                            timeJD=timeJD,
                                            location=location,
                                            numberPoints=numberPoints,
                                            duration=duration,
                                            timeShift=timeShift,
                                            )

        if not suc:
            self.ui.numberDSOPoints.setEnabled(True)
            self.ui.durationDSO.setEnabled(True)
            self.ui.timeShiftDSO.setEnabled(True)
            self.app.message.emit('DSO Path cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        self.ui.numberDSOPoints.setEnabled(True)
        self.ui.durationDSO.setEnabled(True)
        self.ui.timeShiftDSO.setEnabled(True)

        return True

    def genBuildSpiralMax(self):
        """
        genBuildGoldenSpiral generates points along the actual tracking path
        as the processing might take to long (at least on ubuntu), we have to find a
        workaround to this behavior:
        https://stackoverflow.com/questions/41568990/
        how-do-i-prevent-double-valuechanged-events-when-i-press-the-arrows-in-a-qspinbo

        :return: success
        """

        self.lastGenerator = 'spiralMax'

        suc = self.app.data.generateGoldenSpiral(numberPoints=350)
        if not suc:
            self.app.message.emit('Golden spiral cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildSpiralMed(self):
        """

        :return: success
        """

        self.lastGenerator = 'spiralMed'

        suc = self.app.data.generateGoldenSpiral(numberPoints=250)
        if not suc:
            self.app.message.emit('Golden spiral cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildSpiralNorm(self):
        """

        :return: success
        """

        self.lastGenerator = 'spiralNorm'

        suc = self.app.data.generateGoldenSpiral(numberPoints=150)
        if not suc:
            self.app.message.emit('Golden spiral cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildSpiralMin(self):
        """

        :return: success
        """

        self.lastGenerator = 'spiralMin'

        suc = self.app.data.generateGoldenSpiral(numberPoints=75)
        if not suc:
            self.app.message.emit('Golden spiral cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()
        return True

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

        self.lastGenerator = 'file'
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
        self.autoSortPoints()

        return True

    def clearBuildP(self):
        """

        :return: success
        """

        if not self.app.uiWindows['showHemisphereW']['classObj']:
            return False

        self.app.uiWindows['showHemisphereW']['classObj'].clearHemisphere()

        return True

    def autoDeletePoints(self):
        """
        autoDeletePoints removes all generated or visible build points below the horizon line
        or within the limits of the meridian flip and redraws the hemisphere window.

        :return: True for test purpose
        """

        if self.ui.checkAutoDeleteHorizon.isChecked():
            self.app.data.deleteBelowHorizon()

        if self.ui.checkAutoDeleteMeridian.isChecked():
            self.app.data.deleteCloseMeridian()

        self.app.redrawHemisphere.emit()

        return True

    def autoSortPoints(self):
        """
        autoSortPoints sort the given build point first to east and west and than based
        on the decision high altitude to low altitude or east to west in each hemisphere

        :return: success if sorted
        """

        eastwest = self.ui.checkSortEW.isChecked()
        highlow = self.ui.checkSortHL.isChecked()

        if not eastwest and not highlow:
            return False

        self.app.data.sort(eastwest=eastwest, highlow=highlow)
        self.app.redrawHemisphere.emit()

        return True

    def updateSorting(self):
        """

        :return: True for test purpose
        """
        self.autoSortPoints()
        self.app.redrawHemisphere.emit()

        return True
