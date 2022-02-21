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
import json
import os

# external packages
import numpy as np
from scipy.stats.mstats import winsorize

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import analyse_ui


class AnalyseWindow(toolsQtWidget.MWidget):
    """
    the analyse window class handles

    """
    __all__ = ['AnalyseWindow']

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = analyse_ui.Ui_AnalyseDialog()
        self.ui.setupUi(self)
        self.closing = False

        self.latitude = None
        self.pierside = None
        self.countSequence = None
        self.index = None
        self.scaleS = None
        self.altitude = None
        self.azimuth = None
        self.errorAngle = None
        self.errorRMS = None
        self.errorRA_S = None
        self.errorDEC_S = None
        self.errorRA = None
        self.errorDEC = None
        self.angularPosRA = None
        self.angularPosDEC = None

        self.wIcon(self.ui.load, 'load')
        self.modelPositions = self.embedMatplot(self.ui.modelPositions)
        self.errorDistribution = self.embedMatplot(self.ui.errorDistribution)

        self.ui.load.clicked.connect(self.loadModel)
        self.ui.winsorizedLimit.clicked.connect(self.drawAll)
        self.app.colorChange.connect(self.colorChange)

        self.charts = [self.draw_raRawErrors,
                       self.draw_decRawErrors,
                       self.draw_raErrors,
                       self.draw_decError,
                       self.draw_raErrorsRef,
                       self.draw_decErrorsRef,
                       self.draw_raRawErrorsRef,
                       self.draw_decRawErrorsRef,
                       self.draw_scaleImage,
                       self.draw_modelPositions,
                       self.draw_errorAscending,
                       self.draw_errorDistribution]

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'analyseW' not in self.app.config:
            self.app.config['analyseW'] = {}
        config = self.app.config['analyseW']
        height = config.get('height', 800)
        width = config.get('width', 1200)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)
        self.ui.winsorizedLimit.setChecked(config.get('winsorizedLimit', False))
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'analyseW' not in self.app.config:
            self.app.config['analyseW'] = {}

        config = self.app.config['analyseW']
        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        config['winsorizedLimit'] = self.ui.winsorizedLimit.isChecked()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.closing = True
        self.storeConfig()
        self.app.showAnalyse.disconnect(self.showAnalyse)
        super().closeEvent(closeEvent)

    def resizeEvent(self, event):
        """
        we are using the resize event to reset the timer, which means waiting for
        RESIZE_FINISHED_TIMEOUT in total before redrawing the complete hemisphere.
        as we are using a 0.1s cyclic timer.

        :param event:
        :return:
        """
        super().resizeEvent(event)

    def showWindow(self):
        """
        :return: True for test purpose
        """
        self.show()
        self.app.showAnalyse.connect(self.showAnalyse)
        return True

    def colorChange(self):
        """
        :return:
        """
        self.wIcon(self.ui.load, 'load')
        self.setStyleSheet(self.mw4Style)
        self.drawAll()
        return True

    def writeGui(self, data, loadFilePath):
        """
        :param data:
        :param loadFilePath:
        :return: True for test purpose
        """
        d = data[0]
        de = data[-1]

        title = f'Analyse Model     {os.path.basename(loadFilePath)}'
        self.setWindowTitle(title)
        self.ui.eposure.setText(f'{d.get("exposureTime", "")}')
        self.ui.solver.setText(d.get('astrometryApp', ""))
        self.ui.binning.setText(f'{d.get("binning", 0):1.0f}')
        self.ui.time.setText(d.get('julianDate', '').replace('T', '  ').replace('Z', ''))
        self.ui.subframe.setText(f'{d.get("subFrame", 0):3.0f}')
        self.ui.modelTerms.setText(f'{d.get("modelTerms", 0):02.0f}')
        self.ui.modelErrorRMS.setText(f'{d.get("modelErrorRMS", 0):5.1f}')
        self.ui.modelOrthoError.setText(f'{d.get("modelOrthoError", 0):5.0f}')
        self.ui.modelPolarError.setText(f'{d.get("modelPolarError", 0):5.0f}')
        self.ui.focalLength.setText(f'{d.get("focalLength", 0):4.0f}')
        self.ui.profile.setText(f'{d.get("profile", "")}')
        self.ui.firmware.setText(f'{d.get("firmware", "")}')
        self.ui.totalPoints.setText(f'{d.get("lenSequence", 0)}')
        self.ui.goodPoints.setText(f'{de.get("errorIndex", 0)}')
        text = f'{d.get("mirroredS", "")}' + f'{d.get("flippedS", "")}'
        self.ui.mirrored.setText(text)
        version = d.get("version", "").lstrip('MountWizzard4 - v')
        self.ui.version.setText(f'{version}')

        return True

    def generateDataSets(self, modelJSON):
        """
        :param modelJSON:
        :return:
        """
        model = dict()
        for key in modelJSON[0].keys():
            model[key] = list()
            for index in range(0, len(modelJSON)):
                model[key].append(modelJSON[index][key])

        self.latitude = modelJSON[0].get('latitude')
        self.pierside = np.asarray(model['pierside'])
        self.countSequence = np.asarray(model['countSequence'])
        self.index = np.asarray(model['errorIndex']) - 1
        self.scaleS = np.asarray(model['scaleS'])
        self.altitude = np.asarray(model['altitude'])
        self.azimuth = np.asarray(model['azimuth'])
        self.errorAngle = np.asarray(model['errorAngle'])
        self.errorRMS = np.asarray(model['errorRMS'])
        self.errorRA_S = np.asarray(model['errorRA_S'])
        self.errorDEC_S = np.asarray(model['errorDEC_S'])
        self.errorRA = np.asarray(model['errorRA'])
        self.errorDEC = np.asarray(model['errorDEC'])
        self.angularPosRA = np.asarray(model['angularPosRA'])
        self.angularPosDEC = np.asarray(model['angularPosDEC'])
        return True

    def processModel(self, loadFilePath):
        """
        :return: success
        """
        with open(loadFilePath, 'r') as infile:
            modelJSON = json.load(infile)

        self.writeGui(modelJSON, loadFilePath)
        self.generateDataSets(modelJSON)
        self.drawAll()
        return True

    def loadModel(self):
        """
        :return: success
        """
        folder = self.app.mwGlob['modelDir']
        val = self.openFile(self, 'Open model file', folder, 'Model files (*.model)',
                            multiple=False,
                            reverseOrder=True)
        loadFilePath, fileName, ext = val
        if loadFilePath:
            self.processModel(loadFilePath)
        return True

    def showAnalyse(self, path):
        """
        :param path:
        :return: True for test purpose
        """
        if path:
            self.processModel(path)
        return True

    def draw_raRawErrors(self):
        """
        :return:    True if ok for testing
        """
        self.ui.raRawErrors.setLabel('bottom', 'Azimuth [deg]')
        self.ui.raRawErrors.setLabel('left', 'Altitude [deg]')
        self.ui.raRawErrors.plot(self.azimuth, self.altitude, self.errorRA_S)
        return True

    def draw_decRawErrors(self):
        """
        :return:    True if ok for testing
        """
        self.ui.decRawErrors.setLabel('bottom', 'Azimuth [deg]')
        self.ui.decRawErrors.setLabel('left', 'Altitude [deg]')
        self.ui.decRawErrors.plot(self.azimuth, self.altitude, self.errorDEC_S)
        return True

    def draw_raErrors(self):
        """
        :return:    True if ok for testing
        """
        self.ui.raErrors.setLabel('bottom', 'Azimuth [deg]')
        self.ui.raErrors.setLabel('left', 'Altitude [deg]')
        self.ui.raErrors.plot(self.azimuth, self.altitude, self.errorRA)
        return True

    def draw_decError(self):
        """
        :return:    True if ok for testing
        """
        self.ui.decErrors.setLabel('bottom', 'Azimuth [deg]')
        self.ui.decErrors.setLabel('left', 'Altitude [deg]')
        self.ui.decErrors.plot(self.azimuth, self.altitude, self.errorDEC)
        return True

    def draw_raRawErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        self.ui.raRawErrorsRef.setLabel('bottom', 'RA Encoder Abs [deg]')
        self.ui.raRawErrorsRef.setLabel('left', 'Error per Star [arcsec]')
        self.ui.raRawErrorsRef.plot(self.angularPosRA, self.errorRA_S,
                                    self.pierside)
        return True

    def draw_decRawErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        self.ui.decRawErrorsRef.setLabel('bottom', 'DEC Encoder Abs [deg]')
        self.ui.decRawErrorsRef.setLabel('left', 'Error per Star [arcsec]')
        p = self.pierside
        y = self.errorDEC_S
        y = [x if p == 'W' else -x for x, p in zip(y, p)]
        self.ui.decRawErrorsRef.plot(self.angularPosDEC, y, self.pierside, True)
        return True

    def draw_raErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        self.ui.raErrorsRef.setLabel('bottom', 'RA Encoder Abs [deg]')
        self.ui.raErrorsRef.setLabel('left', 'Error per Star [arcsec]')
        self.ui.raErrorsRef.plot(self.angularPosRA, self.errorRA,
                                 self.pierside)
        return True

    def draw_decErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        self.ui.decErrorsRef.setLabel('bottom', 'DEC Encoder Abs [deg]')
        self.ui.decErrorsRef.setLabel('left', 'Error per Star [arcsec]')
        p = self.pierside
        y = self.errorDEC
        y = [x if p == 'W' else -x for x, p in zip(y, p)]
        self.ui.decErrorsRef.plot(self.angularPosDEC, y, self.pierside, True)
        return True

    def draw_scaleImage(self):
        """
        :return:    True if ok for testing
        """
        self.ui.scaleImage.setLabel('bottom', 'Star Number')
        self.ui.scaleImage.setLabel('left', 'Image Scale [arcsec/pix]')
        self.ui.scaleImage.plot(self.index, self.scaleS, self.pierside)
        return True

    def draw_errorAscending(self):
        """
        :return:    True if ok for testing
        """
        self.ui.errorAscending.setLabel('bottom', 'Star')
        self.ui.errorAscending.setLabel('left', 'Error per Star [arcsec]')
        temp = sorted(zip(self.errorRMS, self.pierside))
        y = [x[0] for x in temp]
        p = [x[1] for x in temp]
        self.ui.errorAscending.plot(self.index, y, p)
        return True

    def draw_modelPositions(self):
        """
        :return:    True if ok for testing
        """
        self.ui.modelPositions.plot(self.azimuth, self.altitude, self.errorRMS)
        return True

    def draw_errorDistribution(self):
        """
        :return:    True if ok for testing
        """
        self.ui.errorDistribution.plot(self.errorAngle, self.errorRMS, self.errorRMS)
        return True

    def drawAll(self):
        """
        :return:
        """
        for chart in self.charts:
            if self.closing:
                break
            chart()
        return True
