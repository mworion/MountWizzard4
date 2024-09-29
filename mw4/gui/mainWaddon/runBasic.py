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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import queue
import shutil
import os
import logging

# external packages
from mountcontrol.convert import convertToHMS, convertToDMS
from skyfield.api import Angle

# local import
from base.transform import JNowToJ2000, J2000ToJNow
from gui.utilities.toolsQtWidget import sleepAndEvents
from gui.utilities.qMultiWait import QMultiWait
from base.packageConfig import isSimulationMount


class RunBasic:
    """
    """
    log = logging.getLogger('MW4')

    def __init__(self, mainW):
        self.mainW = mainW
        self.app = mainW.app
        self.ui = mainW.ui
        self.app = mainW.app
        self.msg = mainW.app.msg

    def generateSaveData(self):
        """
        generateSaveData builds from the model file a format which could be
        serialized in json. this format will be used for storing model on file.

        :return: save model format
        """
        modelDataForSave = list()
        for mPoint in self.model:
            sPoint = dict()
            sPoint.update(mPoint)
            sPoint['raJNowM'] = sPoint['raJNowM'].hours
            sPoint['decJNowM'] = sPoint['decJNowM'].degrees
            sPoint['raJ2000M'] = sPoint['raJ2000M'].hours
            sPoint['decJ2000M'] = sPoint['decJ2000M'].degrees
            sPoint['raJNowS'] = sPoint['raJNowS'].hours
            sPoint['decJNowS'] = sPoint['decJNowS'].degrees
            sPoint['raJ2000S'] = sPoint['raJ2000S'].hours
            sPoint['decJ2000S'] = sPoint['decJ2000S'].degrees
            sPoint['haMountModel'] = sPoint['haMountModel'].hours
            sPoint['decMountModel'] = sPoint['decMountModel'].degrees
            sPoint['angularPosRA'] = sPoint['angularPosRA'].degrees
            sPoint['angularPosDEC'] = sPoint['angularPosDEC'].degrees
            sPoint['errorAngle'] = sPoint['errorAngle'].degrees
            sPoint['errorRA'] = sPoint['errorRA'].degrees
            sPoint['errorDEC'] = sPoint['errorDEC'].degrees
            sPoint['modelOrthoError'] = sPoint['modelOrthoError'].degrees
            sPoint['modelPolarError'] = sPoint['modelPolarError'].degrees
            sPoint['altitude'] = sPoint['altitude'].degrees
            sPoint['azimuth'] = sPoint['azimuth'].degrees
            sPoint['siderealTime'] = sPoint['siderealTime'].hours
            sPoint['julianDate'] = sPoint['julianDate'].utc_iso()
            sPoint['version'] = f'{self.app.__version__}'
            sPoint['profile'] = self.ui.profile.text()
            sPoint['firmware'] = self.ui.vString.text()
            sPoint['latitude'] = self.app.mount.obsSite.location.latitude.degrees
            modelDataForSave.append(sPoint)
        return modelDataForSave

    def setupRunPoints(self, data=None, imgDir='', name='', waitTime=0):
        """
        :param data:
        :param imgDir:
        :param name:
        :param waitTime:
        :return:
        """
        if data is None:
            data = []
        plateSolveApp = self.ui.plateSolveDevice.currentText()
        exposureTime = self.ui.exposureTime1.value()
        binning = int(self.ui.binning1.value())
        subFrame = self.ui.subFrame.value()
        fastReadout = self.ui.fastDownload.isChecked()
        focalLength = self.ui.focalLength.value()
        lenSequence = len(data)
        framework = self.app.plateSolve.framework
        solveTimeout = self.app.plateSolve.run[framework].timeout
        searchRadius = self.app.plateSolve.run[framework].searchRadius
        modelPoints = list()
        for index, point in enumerate(data):
            m = dict()
            imagePath = f'{imgDir}/image-{index + 1:03d}.fits'
            m['imagePath'] = imagePath
            m['exposureTime'] = exposureTime
            m['binning'] = binning
            m['subFrame'] = subFrame
            m['fastReadout'] = fastReadout
            m['lenSequence'] = lenSequence
            m['countSequence'] = index + 1
            m['pointNumber'] = index + 1
            m['name'] = name
            m['plateSolveApp'] = plateSolveApp
            m['solveTimeout'] = solveTimeout
            m['searchRadius'] = searchRadius
            m['focalLength'] = focalLength
            m['altitude'] = Angle(degrees=point[0])
            m['azimuth'] = Angle(degrees=point[1])
            m['waitTime'] = waitTime
            modelPoints.append(m)
        return modelPoints
