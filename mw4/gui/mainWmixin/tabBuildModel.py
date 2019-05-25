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
import queue
import os
# external packages
import PyQt5.QtWidgets
import PyQt5.uic
# local import
from mw4.definitions import Point, MPoint, IParam


class QMultiWait(PyQt5.QtCore.QObject):
    """
    QMultiWaitable implements a signal collection class for waiting of entering multiple
    signals before firing the "AND" relation of all signals.
    derived from:

    https://stackoverflow.com/questions/21108407/qt-how-to-wait-for-multiple-signals

    in addition all received signals could be reset
    """

    ready = PyQt5.QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.waitable = set()
        self.waitready = set()

    def addWaitableSignal(self, signal):
        if signal not in self.waitable:
            self.waitable.add(signal)
            signal.connect(self.checkSignal)

    def checkSignal(self):
        sender = self.sender()
        self.waitready.add(sender)
        if len(self.waitready) == len(self.waitable):
            self.ready.emit()

    def resetSignals(self):
        self.waitready = set()

    def clear(self):
        for signal in self.waitable:
            signal.disconnect(self.checkSignal)


class BuildModel(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):

        self.slewQueue = queue.Queue()
        self.imageQueue = queue.Queue()
        self.solveQueue = queue.Queue()

        self.collector = QMultiWait()

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
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.durationDSO.valueChanged.connect(self.genBuildDSO)
        self.ui.timeShiftDSO.valueChanged.connect(self.genBuildDSO)
        self.ui.saveBuildPoints.clicked.connect(self.saveBuildFile)
        self.ui.saveBuildPointsAs.clicked.connect(self.saveBuildFileAs)
        self.ui.loadBuildPoints.clicked.connect(self.loadBuildFile)
        self.ui.numberSpiralPoints.valueChanged.connect(self.genBuildGoldenSpiral)
        self.ui.genBuildGoldenSpiral.clicked.connect(self.genBuildGoldenSpiral)

        self.ui.runFullModel.clicked.connect(self.modelFull)

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
        """
        genBuildDSO generates points along the actual tracking path

        :return: success
        """

        ra = self.app.mount.obsSite.raJNow
        dec = self.app.mount.obsSite.decJNow
        timeJD = self.app.mount.obsSite.timeJD
        location = self.app.mount.obsSite.location

        if ra is None or dec is None or location is None:
            self.app.message.emit('DSO Path cannot be generated', 2)
            return False

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
            self.app.message.emit('DSO Path cannot be generated', 2)
            return False
        self.autoDeletePoints()
        self.autoSortPoints()
        return True

    def genBuildGoldenSpiral(self):
        """
        genBuildGoldenSpiral generates points along the actual tracking path

        :return: success
        """

        numberPoints = self.ui.numberSpiralPoints.value()

        suc = self.app.data.generateGoldenSpiral(numberPoints=numberPoints,
                                                 )

        if not suc:
            self.app.message.emit('DSO Path cannot be generated', 2)
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

    def exposeImage(self, imagePath='', expTime=0, binning=0, subFrame=0, fast=True):
        """
        exposeImage gathers all necessary parameters and starts exposing

        :param imagePath:
        :param expTime:
        :param binning:
        :param subFrame:
        :param fast:
        :return: True for test purpose
        """

        self.app.imaging.expose(imagePath=imagePath,
                                expTime=expTime,
                                binning=binning,
                                subFrame=subFrame,
                                )

        return True

    def modelSolve(self):
        """

        :return:
        """

        if self.solveQueue.empty():
            return False

        mpoint = self.solveQueue.get()
        self.ui.mSolved.setText(f'{mpoint.number:02d}')
        print(mpoint)
        return
        self.app.imageW.solveImage()

    def modelImage(self):
        """

        :return:
        """

        if self.imageQueue.empty():
            return False

        mpoint = self.imageQueue.get()
        self.collector.resetSignals()
        self.exposeImage(imagePath=mpoint.path,
                         expTime=mpoint.param.expTime,
                         binning=mpoint.param.binning,
                         subFrame=mpoint.param.subFrame,
                         )
        self.ui.mImaged.setText(f'{mpoint.number:02d}')
        self.solveQueue.put(mpoint)

    def modelSlew(self):
        """

        :return:
        """

        if self.slewQueue.empty():
            return False

        mpoint = self.slewQueue.get()
        self.app.dome.slewToAltAz(azimuth=mpoint.point.azimuth)
        suc = self.app.mount.obsSite.slewAltAz(alt_degrees=mpoint.point.altitude,
                                               az_degrees=mpoint.point.azimuth,
                                               )
        self.ui.mSlewed.setText(f'{mpoint.number:02d}')
        self.imageQueue.put(mpoint)

        return True

    def modelFull(self):
        """

        :return: success
        """

        expTime = self.app.mainW.ui.expTime.value()
        binning = self.app.mainW.ui.binning.value()
        subFrame = self.app.mainW.ui.subFrame.value()

        time = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        directory = f'{self.app.mwGlob["imageDir"]}/{time}'
        os.mkdir(directory)
        if not os.path.isdir(directory):
            return False

        self.collector.addWaitableSignal(self.app.dome.signals.slewFinished)
        self.collector.addWaitableSignal(self.app.mount.signals.slewFinished)
        self.collector.ready.connect(self.modelImage)
        self.app.imaging.signals.saved.connect(self.modelSolve)
        self.app.imaging.signals.integrated.connect(self.modelSlew)

        points = [Point(altitude=50, azimuth=30),
                  Point(altitude=55, azimuth=40),
                  Point(altitude=50, azimuth=50)]

        self.ui.mPoints.setText(f'{len(points):02d}')
        for number, point in enumerate(points):
            # define the path to the image file
            imagePath = f'{directory}/modelimage-{number:03d}.fits'

            # image parameters
            param = IParam(expTime=expTime,
                           binning=binning,
                           subFrame=subFrame,
                           fast=True,
                           )

            # transfer to working in a queue with necessary data
            self.slewQueue.put(MPoint(number=number + 1,
                                      path=imagePath,
                                      param=param,
                                      point=point))

        self.modelSlew()
