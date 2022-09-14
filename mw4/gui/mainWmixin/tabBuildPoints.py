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
from PyQt5.QtCore import QMutex
from astroquery.simbad import Simbad

# local import
from base.tpool import Worker
from mountcontrol.convert import convertRaToAngle, convertDecToAngle
from mountcontrol.convert import formatHstrToText, formatDstrToText


class BuildPoints:
    """
    """

    def __init__(self):
        self.sortRunning = QMutex()
        self.lastGenerator = 'none'
        self.sortedGenerators = {
            'grid': self.genBuildGrid,
            'align3': self.genBuildAlign3,
            'align6': self.genBuildAlign6,
            'align9': self.genBuildAlign9,
            'align12': self.genBuildAlign12,
            'max': self.genBuildMax,
            'med': self.genBuildMed,
            'norm': self.genBuildNorm,
            'min': self.genBuildMin,
            'dso': self.genBuildDSO,
            'file': self.genBuildFile,
            'model': self.genModel,
        }
        self.simbadRa = None
        self.simbadDec = None

        self.ui.genBuildGrid.clicked.connect(self.genBuildGrid)
        self.ui.genBuildAlign3.clicked.connect(self.genBuildAlign3)
        self.ui.genBuildAlign6.clicked.connect(self.genBuildAlign6)
        self.ui.genBuildAlign9.clicked.connect(self.genBuildAlign9)
        self.ui.genBuildAlign12.clicked.connect(self.genBuildAlign12)
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
        self.ui.genModel.clicked.connect(self.genModel)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.saveBuildPoints.clicked.connect(self.saveBuildFile)
        self.ui.saveBuildPointsAs.clicked.connect(self.saveBuildFileAs)
        self.ui.loadBuildPoints.clicked.connect(self.loadBuildFile)
        self.ui.genBuildSpiral.clicked.connect(self.genBuildGoldenSpiral)
        self.ui.clearBuildP.clicked.connect(self.clearBuildP)
        self.ui.sortNothing.clicked.connect(self.rebuildPoints)
        self.ui.sortEW.clicked.connect(self.rebuildPoints)
        self.ui.sortHL.clicked.connect(self.rebuildPoints)
        self.ui.ditherBuildPoints.clicked.connect(self.rebuildPoints)
        self.ui.avoidFlip.clicked.connect(self.rebuildPoints)
        self.ui.autoDeleteMeridian.clicked.connect(self.rebuildPoints)
        self.ui.autoDeleteHorizon.clicked.connect(self.rebuildPoints)
        self.app.buildPointsChanged.connect(self.buildPointsChanged)
        self.ui.generateQuery.editingFinished.connect(self.querySimbad)
        self.ui.isOnline.stateChanged.connect(self.setupDsoGui)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']

        self.ui.numberGridPointsCol.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.disconnect(self.genBuildDSO)

        self.ui.buildPFileName.setText(config.get('buildPFileName', ''))
        self.ui.numberGridPointsRow.setValue(config.get('numberGridPointsRow', 5))
        self.ui.numberGridPointsCol.setValue(config.get('numberGridPointsCol', 6))
        self.ui.altitudeMin.setValue(config.get('altitudeMin', 30))
        self.ui.altitudeMax.setValue(config.get('altitudeMax', 75))
        self.ui.numberDSOPoints.setValue(config.get('numberDSOPoints', 15))
        self.ui.numberSpiral.setValue(config.get('numberSpiral', 30))

        self.ui.autoDeleteMeridian.setChecked(config.get('autoDeleteMeridian', False))
        self.ui.autoDeleteHorizon.setChecked(config.get('autoDeleteHorizon', True))
        self.ui.useSafetyMargin.setChecked(config.get('useSafetyMargin', False))
        self.ui.safetyMarginValue.setValue(config.get('safetyMarginValue', 0))
        self.ui.avoidFlip.setChecked(config.get('avoidFlip', False))
        self.ui.sortNothing.setChecked(config.get('sortNothing', True))
        self.ui.sortEW.setChecked(config.get('sortEW', False))
        self.ui.useDomeAz.setChecked(config.get('useDomeAz', False))
        self.ui.sortHL.setChecked(config.get('sortHL', False))
        self.ui.keepGeneratedPoints.setChecked(config.get('keepGeneratedPoints', False))
        self.ui.ditherBuildPoints.setChecked(config.get('ditherBuildPoints', False))

        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.setupDsoGui()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['buildPFileName'] = self.ui.buildPFileName.text()
        config['numberGridPointsRow'] = self.ui.numberGridPointsRow.value()
        config['numberGridPointsCol'] = self.ui.numberGridPointsCol.value()
        config['altitudeMin'] = self.ui.altitudeMin.value()
        config['altitudeMax'] = self.ui.altitudeMax.value()
        config['numberDSOPoints'] = self.ui.numberDSOPoints.value()
        config['numberSpiral'] = self.ui.numberSpiral.value()
        config['autoDeleteMeridian'] = self.ui.autoDeleteMeridian.isChecked()
        config['autoDeleteHorizon'] = self.ui.autoDeleteHorizon.isChecked()
        config['useSafetyMargin'] = self.ui.useSafetyMargin.isChecked()
        config['safetyMarginValue'] = self.ui.safetyMarginValue.value()
        config['avoidFlip'] = self.ui.avoidFlip.isChecked()
        config['sortNothing'] = self.ui.sortNothing.isChecked()
        config['sortEW'] = self.ui.sortEW.isChecked()
        config['useDomeAz'] = self.ui.useDomeAz.isChecked()
        config['sortHL'] = self.ui.sortHL.isChecked()
        config['keepGeneratedPoints'] = self.ui.keepGeneratedPoints.isChecked()
        config['ditherBuildPoints'] = self.ui.ditherBuildPoints.isChecked()

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
        keep = self.ui.keepGeneratedPoints.isChecked()

        suc = self.app.data.genGrid(minAlt=minAlt,
                                    maxAlt=maxAlt,
                                    numbRows=row,
                                    numbCols=col,
                                    keep=keep)

        if not suc:
            self.ui.numberGridPointsRow.setEnabled(True)
            self.ui.numberGridPointsCol.setEnabled(True)
            self.ui.altitudeMin.setEnabled(True)
            self.ui.altitudeMax.setEnabled(True)
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Could not generate grid')
            return False

        self.processPoints()
        self.ui.numberGridPointsRow.setEnabled(True)
        self.ui.numberGridPointsCol.setEnabled(True)
        self.ui.altitudeMin.setEnabled(True)
        self.ui.altitudeMax.setEnabled(True)
        return True

    def genBuildAlign3(self):
        """
        genBuildAlign3 generates a grid of 3 point for model build based on gui
        data.

        :return: success
        """
        self.lastGenerator = 'align3'
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genAlign(altBase=55,
                                     azBase=10,
                                     numberBase=3,
                                     keep=keep)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Could not generate 3 align stars')
            return False

        self.processPoints()
        return True

    def genBuildAlign6(self):
        """
        genBuildAlign6 generates a grid of 6 point for model build based on gui
        data.

        :return: success
        """
        self.lastGenerator = 'align6'
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genAlign(altBase=55,
                                     azBase=10,
                                     numberBase=6,
                                     keep=keep)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Could not generate 6 align stars')
            return False

        self.processPoints()
        return True

    def genBuildAlign9(self):
        """
        genBuildAlign9 generates a grid of 9 point for model build based on gui
        data.

        :return: success
        """
        self.lastGenerator = 'align9'
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genAlign(altBase=55,
                                     azBase=10,
                                     numberBase=9,
                                     keep=keep)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Could not generate 9 align stars')
            return False

        self.processPoints()
        return True

    def genBuildAlign12(self):
        """
        genBuildAlign12 generates a grid of 12 point for model build based on gui
        data.

        :return: success
        """
        self.lastGenerator = 'align12'
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genAlign(altBase=55,
                                     azBase=10,
                                     numberBase=12,
                                     keep=keep)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Could not generate 12 align stars')
            return False

        self.processPoints()
        return True

    def genBuildMax(self):
        """
        genBuildMax generates the point pattern based on greater circles for
        model build. the point are calculated for the observers position. max
        goes for approx 100 points effectively when removing the horizon.

        :return: success
        """
        self.lastGenerator = 'max'
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genGreaterCircle(selection='max', keep=keep)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Build points [max] cannot be generated')
            return False

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()
        return True

    def genBuildMed(self):
        """
        genBuildMed generates the point pattern based on greater circles for
        model build. the point are calculated for the observers position. max
        goes for approx 70 points effectively when removing the horizon.

        :return: success
        """
        self.lastGenerator = 'med'
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genGreaterCircle(selection='med', keep=keep)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Build points [med] cannot be generated')
            return False

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()
        return True

    def genBuildNorm(self):
        """
        genBuildNorm generates the point pattern based on greater circles for
        model build. the point are calculated for the observers position. max
        goes for approx 40 points effectively when removing the horizon.

        :return: success
        """
        self.lastGenerator = 'norm'
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genGreaterCircle(selection='norm', keep=keep)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Build points [norm] cannot be generated')
            return False

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()
        return True

    def genBuildMin(self):
        """
        genBuildMin generates the point pattern based on greater circles for
        model build. the point are calculated for the observers position. min
        goes for approx 25 points effectively when removing the horizon.

        :return: success
        """
        self.lastGenerator = 'min'
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genGreaterCircle(selection='min', keep=keep)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Build points [min] cannot be generated')
            return False

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()
        return True

    def genBuildDSO(self):
        """
        genBuildDSO generates points along the actual tracking path

        :return: success
        """
        self.lastGenerator = 'dso'
        ha = self.app.mount.obsSite.raJNow
        dec = self.app.mount.obsSite.decJNow
        lst = self.app.mount.obsSite.timeSidereal
        timeJD = self.app.mount.obsSite.timeJD
        location = self.app.mount.obsSite.location

        if ha is None or dec is None or location is None or lst is None:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'DSO Path cannot be generated - mount off')
            return False

        if self.simbadRa and self.simbadDec:
            ha = self.simbadRa
            dec = self.simbadDec

        self.ui.numberDSOPoints.setEnabled(False)
        numberPoints = self.ui.numberDSOPoints.value()
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.generateDSOPath(ha=ha,
                                            dec=dec,
                                            timeJD=timeJD,
                                            location=location,
                                            numberPoints=numberPoints,
                                            keep=keep)
        if not suc:
            self.ui.numberDSOPoints.setEnabled(True)
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'DSO Path cannot be generated - calc error')
            return False

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()
        self.ui.numberDSOPoints.setEnabled(True)
        return True

    def genBuildGoldenSpiral(self):
        """
        genBuildGoldenSpiral generates points along the actual tracking path
        as the processing might take to long (at least on ubuntu), we have to
        find a workaround to this behavior:
        https://stackoverflow.com/questions/41568990/
        how-do-i-prevent-double-valuechanged-events-when-i-press-the-arrows-in-a-qspinbo

        :return: success
        """
        self.lastGenerator = 'spiral'
        numberTarget = int(self.ui.numberSpiral.value())
        self.changeStyleDynamic(self.ui.genBuildSpiral, 'running', True)
        numberPoints = 0
        numberFilter = 0
        while numberFilter < numberTarget:
            numberPoints = numberPoints + numberTarget - numberFilter
            suc = self.app.data.generateGoldenSpiral(numberPoints=numberPoints)
            if not suc:
                break
            self.processPoints()
            numberFilter = len(self.app.data.buildP)
        self.changeStyleDynamic(self.ui.genBuildSpiral, 'running', False)
        if not suc:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Golden spiral cannot be generated')
            return False
        return True

    def genModel(self):
        """
        :return: success
        """
        self.lastGenerator = 'model'

        keep = self.ui.keepGeneratedPoints.isChecked()
        if not keep:
            self.app.data.clearBuildP()

        model = self.app.mount.model
        for star in model.starList:
            self.app.data.addBuildP((star.alt.degrees, star.az.degrees, True))

        self.processPoints()
        return True

    def genBuildFile(self):
        """
        genBuildFile tries to load a give build point file and displays it for usage.

        :return: success
        """
        self.lastGenerator = 'file'
        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          'Build points file name not given')
            return False

        keep = self.ui.keepGeneratedPoints.isChecked()
        fullFileName = self.app.mwGlob['configDir'] + '/' + fileName + '.bpts'
        suc = self.app.data.loadBuildP(fullFileName=fullFileName, keep=keep)

        if not suc:
            text = f'Build points file [{fileName}] could not be loaded'
            self.msg.emit(2, 'Model', 'Buildpoints', text)
            return False

        self.processPoints()
        return True

    def loadBuildFile(self):
        """
        :return: success
        """
        folder = self.app.mwGlob['configDir']
        fileTypes = 'Build Point Files (*.bpts)'
        fileTypes += ';; CSV Files (*.csv)'
        fileTypes += ';; Model Files (*.model)'
        fullFileName, fileName, ext = self.openFile(
            self, 'Open build point file', folder, fileTypes)
        if not fullFileName:
            return False

        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.loadBuildP(fullFileName=fullFileName, ext=ext, keep=keep)
        if suc:
            self.ui.buildPFileName.setText(fileName)
            self.msg.emit(0, 'Model', 'Buildpoints',
                          f'Build file [{fileName}] loaded')
        else:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          f'Build file [{fileName}] cannot be loaded')
        self.genBuildFile()
        return True

    def saveBuildFile(self):
        """
        :return: success
        """
        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.msg.emit(0, 'Model', 'Buildpoints',
                          'Build points file name not given')
            return False

        suc = self.app.data.saveBuildP(fileName=fileName)
        if suc:
            self.msg.emit(0, 'Model', 'Buildpoints',
                          f'Build file [{fileName}] saved')
        else:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          f'Build file [{fileName}] cannot be saved')

        return True

    def saveBuildFileAs(self):
        """
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
            self.msg.emit(0, 'Model', 'Buildpoints',
                          f'Build file [{fileName}] saved')
        else:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          f'Build file [{fileName}] cannot be saved')

        return True

    def clearBuildP(self):
        """
        :return: success
        """
        self.app.data.clearBuildP()
        self.app.drawBuildPoints.emit()
        if not self.app.uiWindows['showHemisphereW']['classObj']:
            return False

        self.app.redrawHemisphere.emit()
        return True

    def autoDeletePoints(self):
        """
        autoDeletePoints removes all generated or visible build points below the
        horizon line or within the limits of the meridian flip and redraws the
        hemisphere window.

        :return: True for test purpose
        """
        if self.ui.autoDeleteHorizon.isChecked():
            self.app.data.deleteBelowHorizon()
        if self.ui.autoDeleteMeridian.isChecked():
            self.app.data.deleteCloseMeridian()
        if self.ui.useSafetyMargin.isChecked():
            value = self.ui.safetyMarginValue.value()
            self.app.data.deleteCloseHorizonLine(value)
        return True

    def doSortDomeAzData(self, result):
        """
        :param result:
        :return:
        """
        points, pierside = result
        self.app.data.sort(points=points,
                           sortDomeAz=True,
                           pierside=pierside)
        self.sortRunning.unlock()
        self.app.redrawHemisphere.emit()
        self.app.drawBuildPoints.emit()
        return True

    def sortDomeAzWorker(self, points, pierside=None):
        """
        :param points:
        :param pierside:
        :return:
        """
        pointsNew = list()
        numbAll = len(points)
        ui = self.ui.autoSortGroup
        self.changeStyleDynamic(ui, 'running', True)
        for i, point in enumerate(points):
            t = f'Auto sort points: progress {(i + 1) / numbAll * 100:3.0f}%'
            ui.setTitle(t)
            alt = point[0]
            az = point[1]
            _, domeAz = self.app.mount.calcMountAltAzToDomeAltAz(alt, az)
            if domeAz is None:
                continue
            pointsNew.append((alt, az, True, domeAz.degrees))
        points = pointsNew
        ui.setTitle('Auto sort points')
        self.changeStyleDynamic(ui, 'running', False)
        return points, pierside

    def sortDomeAz(self, points, pierside=None):
        """
        :param points:
        :param pierside:
        :return:
        """
        if not self.sortRunning.tryLock():
            return False
        worker = Worker(self.sortDomeAzWorker, points, pierside)
        worker.signals.result.connect(self.doSortDomeAzData)
        self.threadPool.start(worker)
        return True

    def sortMountAz(self, points, eastwest=None, highlow=None, pierside=None):
        """
        :param points:
        :param eastwest:
        :param highlow:
        :param pierside:
        :return:
        """
        points = [(x[0], x[1], x[2], 0) for x in points]
        self.app.data.sort(points=points,
                           eastwest=eastwest,
                           highlow=highlow,
                           pierside=pierside)
        self.app.redrawHemisphere.emit()
        self.app.drawBuildPoints.emit()
        return True

    def autoSortPoints(self):
        """
        autoSortPoints sort the given build point first to east and west and
        then based on the decision high altitude to low altitude or east to west
        in each hemisphere

        :return: success if sorted
        """
        eastwest = self.ui.sortEW.isChecked()
        highlow = self.ui.sortHL.isChecked()
        avoidFlip = self.ui.avoidFlip.isChecked()
        useDomeAz = self.ui.useDomeAz.isChecked()
        enableDomeAz = self.ui.useDomeAz.isEnabled()
        noSort = self.ui.sortNothing.isChecked()
        pierside = self.app.mount.obsSite.pierside

        if not avoidFlip:
            pierside = None

        points = self.app.data.buildP
        if noSort and not avoidFlip:
            self.app.redrawHemisphere.emit()
            self.app.drawBuildPoints.emit()
            return False

        if useDomeAz and enableDomeAz and eastwest:
            self.sortDomeAz(points=points, pierside=pierside)
        else:
            self.sortMountAz(points=points, eastwest=eastwest, highlow=highlow,
                             pierside=pierside)

        return True

    def buildPointsChanged(self):
        """
        :return:
        """
        self.lastGenerator = 'none'
        return True

    def rebuildPoints(self):
        """
        :return:
        """
        if self.lastGenerator in self.sortedGenerators:
            self.sortedGenerators[self.lastGenerator]()
        self.processPoints()
        return True

    def processPoints(self):
        """
        :return: True for test purpose
        """
        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def setupDsoGui(self):
        """
        :return:
        """
        isOnline = self.ui.isOnline.isChecked()
        self.ui.generateQuery.setEnabled(isOnline)
        self.ui.generateRa.setEnabled(isOnline)
        self.ui.generateDec.setEnabled(isOnline)
        self.ui.generateQueryText.setEnabled(isOnline)
        self.ui.generateRaText.setEnabled(isOnline)
        self.ui.generateDecText.setEnabled(isOnline)
        return True

    def querySimbad(self):
        """
        :return:
        """
        if not self.ui.isOnline.isChecked():
            self.msg.emit(2, 'Model', 'Buildpoints', 'MW4 is offline')
            return False

        ident = self.ui.generateQuery.text().strip()
        if not ident:
            self.msg.emit(2, 'Model', 'Buildpoints', 'No query data given')
            self.ui.generateRa.setText('')
            self.ui.generateDec.setText('')
            self.simbadRa = None
            self.simbadDec = None
            return False

        result = Simbad.query_object(ident)

        if not result:
            self.msg.emit(2, 'Model', 'Buildpoints',
                          f'No response from SIMBAD for {ident}')
            self.ui.generateRa.setText('')
            self.ui.generateDec.setText('')
            self.simbadRa = None
            self.simbadDec = None
            return False

        self.simbadRa = convertRaToAngle(result['RA'].value.data[0])
        text = formatHstrToText(self.simbadRa)
        self.ui.generateRa.setText(text)

        self.simbadDec = convertDecToAngle(result['DEC'].value.data[0])
        text = formatDstrToText(self.simbadDec)
        self.ui.generateDec.setText(text)
        return True
