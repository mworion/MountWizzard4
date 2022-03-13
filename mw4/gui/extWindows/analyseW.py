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

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import analyse_ui


class AnalyseWindow(toolsQtWidget.MWidget):
    """
    the analysis window class handles

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
        self.ui.load.clicked.connect(self.loadModel)
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
        self.ui.showHorizon.setChecked(config.get('showHorizon', False))
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
        config['showHorizon'] = self.ui.showHorizon.isChecked()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.closing = True
        self.storeConfig()
        self.app.showAnalyse.disconnect(self.showAnalyse)
        self.ui.showHorizon.clicked.disconnect(self.drawAll)
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return: True for test purpose
        """
        self.show()
        self.app.showAnalyse.connect(self.showAnalyse)
        self.ui.showHorizon.clicked.connect(self.drawAll)
        return True

    def colorChange(self):
        """
        :return:
        """
        self.wIcon(self.ui.load, 'load')
        self.setStyleSheet(self.mw4Style)
        for plot in [self.ui.raRawErrors, self.ui.decRawErrors, self.ui.raErrors,
                     self.ui.decErrors, self.ui.raRawErrorsRef,
                     self.ui.decRawErrorsRef, self.ui.raErrorsRef,
                     self.ui.decErrorsRef, self.ui.scaleImage,
                     self.ui.modelPositions, self.ui.errorAscending,
                     self.ui.errorDistribution]:
            plot.colorChange()
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
        self.pierside = np.array(model['pierside'])
        self.countSequence = np.array(model['countSequence'], dtype=np.int64)
        self.index = np.array(model['errorIndex'], dtype=np.int64) - 1
        self.scaleS = np.array(model['scaleS'], dtype=np.float32)
        self.altitude = np.array(model['altitude'], dtype=np.float32)
        self.azimuth = np.array(model['azimuth'], dtype=np.float32)
        self.errorAngle = np.array(model['errorAngle'], dtype=np.float32)
        self.errorRMS = np.array(model['errorRMS'], dtype=np.float32)
        self.errorRA_S = np.array(model['errorRA_S'], dtype=np.float32)
        self.errorDEC_S = np.array(model['errorDEC_S'], dtype=np.float32)
        self.errorRA = np.array(model['errorRA'], dtype=np.float32)
        self.errorDEC = np.array(model['errorDEC'], dtype=np.float32)
        self.angularPosRA = np.array(model['angularPosRA'], dtype=np.float32)
        self.angularPosDEC = np.array(model['angularPosDEC'], dtype=np.float32)
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
        self.ui.raRawErrors.p[0].setLabel('bottom', 'Azimuth [deg]')
        self.ui.raRawErrors.p[0].setLabel('left', 'Altitude [deg]')
        ticks = [(x, f'{x}') for x in range(30, 360, 30)]
        self.ui.raRawErrors.p[0].getAxis('bottom').setTicks([ticks])
        self.ui.raRawErrors.p[0].getAxis('top').setTicks([ticks])
        self.ui.raRawErrors.plot(
            self.azimuth, self.altitude, z=self.errorRA_S, data=self.errorRA_S,
            range={'xMin': 0, 'yMin': 0, 'xMax': 360, 'yMax': 90},
            tip='Az: {x:0.0f}\nAlt: {y:0.1f}\nError: {data:0.1f}'.format)
        if self.ui.showHorizon.isChecked():
            self.ui.raRawErrors.drawHorizon(self.app.data.horizonP)
        return True

    def draw_decRawErrors(self):
        """
        :return:    True if ok for testing
        """
        self.ui.decRawErrors.p[0].setLabel('bottom', 'Azimuth [deg]')
        self.ui.decRawErrors.p[0].setLabel('left', 'Altitude [deg]')
        ticks = [(x, f'{x}') for x in range(30, 360, 30)]
        self.ui.decRawErrors.p[0].getAxis('bottom').setTicks([ticks])
        self.ui.decRawErrors.p[0].getAxis('top').setTicks([ticks])
        self.ui.decRawErrors.plot(
            self.azimuth, self.altitude, z=self.errorDEC_S, data=self.errorDEC_S,
            range={'xMin': 0, 'yMin': 0, 'xMax': 360, 'yMax': 90},
            tip='Az: {x:0.0f}\nAlt: {y:0.1f}\nError: {data:0.1f}'.format)
        if self.ui.showHorizon.isChecked():
            self.ui.decRawErrors.drawHorizon(self.app.data.horizonP)
        return True

    def draw_raErrors(self):
        """
        :return:    True if ok for testing
        """
        self.ui.raErrors.p[0].setLabel('bottom', 'Azimuth [deg]')
        self.ui.raErrors.p[0].setLabel('left', 'Altitude [deg]')
        ticks = [(x, f'{x}') for x in range(30, 360, 30)]
        self.ui.raErrors.p[0].getAxis('bottom').setTicks([ticks])
        self.ui.raErrors.p[0].getAxis('top').setTicks([ticks])
        self.ui.raErrors.plot(
            self.azimuth, self.altitude, z=self.errorRA, data=self.errorRA,
            range={'xMin': 0, 'yMin': 0, 'xMax': 360, 'yMax': 90},
            tip='Az: {x:0.0f}\nAlt: {y:0.1f}\nError: {data:0.1f}'.format)
        if self.ui.showHorizon.isChecked():
            self.ui.raErrors.drawHorizon(self.app.data.horizonP)
        return True

    def draw_decError(self):
        """
        :return:    True if ok for testing
        """
        self.ui.decErrors.p[0].setLabel('bottom', 'Azimuth [deg]')
        self.ui.decErrors.p[0].setLabel('left', 'Altitude [deg]')
        ticks = [(x, f'{x}') for x in range(30, 360, 30)]
        self.ui.decErrors.p[0].getAxis('bottom').setTicks([ticks])
        self.ui.decErrors.p[0].getAxis('top').setTicks([ticks])
        self.ui.decErrors.plot(
            self.azimuth, self.altitude, z=self.errorDEC, data=self.errorDEC,
            range={'xMin': 0, 'yMin': 0, 'xMax': 360, 'yMax': 90},
            tip='Az: {x:0.0f}\nAlt: {y:0.1f}\nError: {data:0.1f}'.format)
        if self.ui.showHorizon.isChecked():
            self.ui.decErrors.drawHorizon(self.app.data.horizonP)
        return True

    def draw_raRawErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        self.ui.raRawErrorsRef.p[0].setLabel('bottom', 'RA Encoder Abs [deg]')
        self.ui.raRawErrorsRef.p[0].setLabel('left', 'Error per Star [arcsec]')
        ticks = [(x, f'{x}') for x in range(30, 180, 30)]
        self.ui.raRawErrorsRef.p[0].getAxis('bottom').setTicks([ticks])
        self.ui.raRawErrorsRef.p[0].getAxis('top').setTicks([ticks])
        color = [self.M_GREEN if p == 'W' else self.M_YELLOW for p in self.pierside]
        self.ui.raRawErrorsRef.plot(
            self.angularPosRA, self.errorRA_S, color=color,
            range={'xMin': 0, 'xMax': 180}, data=self.pierside,
            tip='AngularRA: {x:0.1f}\nErrorRa: {y:0.1f}\nPier: {data}'.format)
        return True

    def draw_decRawErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        self.ui.decRawErrorsRef.p[0].setLabel('bottom', 'DEC Encoder Abs [deg]')
        self.ui.decRawErrorsRef.p[0].setLabel('left', 'Error per Star [arcsec]')
        ticks = [(x, f'{x}') for x in range(-80, 90, 20)]
        self.ui.decRawErrorsRef.p[0].getAxis('bottom').setTicks([ticks])
        self.ui.decRawErrorsRef.p[0].getAxis('top').setTicks([ticks])
        y = [x if p == 'W' else -x for x, p in zip(self.errorDEC_S, self.pierside)]
        color = [self.M_GREEN if p == 'W' else self.M_YELLOW for p in self.pierside]
        self.ui.decRawErrorsRef.plot(
            self.angularPosDEC, y, color=color,
            range={'xMin': -90, 'xMax': 90}, data=self.pierside,
            tip='AngularDEC: {x:0.1f}\nErrorDec: {y:0.1f}\nPier: {data}'.format)
        return True

    def draw_raErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        self.ui.raErrorsRef.p[0].setLabel('bottom', 'RA Encoder Abs [deg]')
        self.ui.raErrorsRef.p[0].setLabel('left', 'Error per Star [arcsec]')
        ticks = [(x, f'{x}') for x in range(30, 180, 30)]
        self.ui.raErrorsRef.p[0].getAxis('bottom').setTicks([ticks])
        self.ui.raErrorsRef.p[0].getAxis('top').setTicks([ticks])
        color = [self.M_GREEN if p == 'W' else self.M_YELLOW for p in self.pierside]
        self.ui.raErrorsRef.plot(
            self.angularPosRA, self.errorRA, color=color,
            range={'xMin': 0, 'xMax': 180}, data=self.pierside,
            tip='AngularRA: {x:0.1f}\nErrorRA: {y:0.1f}\nPier: {data}'.format)
        return True

    def draw_decErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        self.ui.decErrorsRef.p[0].setLabel('bottom', 'DEC Encoder Abs [deg]')
        self.ui.decErrorsRef.p[0].setLabel('left', 'Error per Star [arcsec]')
        ticks = [(x, f'{x}') for x in range(-80, 90, 20)]
        self.ui.decErrorsRef.p[0].getAxis('bottom').setTicks([ticks])
        self.ui.decErrorsRef.p[0].getAxis('top').setTicks([ticks])
        y = [x if p == 'W' else -x for x, p in zip(self.errorDEC, self.pierside)]
        color = [self.M_GREEN if p == 'W' else self.M_YELLOW for p in self.pierside]
        self.ui.decErrorsRef.plot(
            self.angularPosDEC, y, color=color,
            range={'xMin': -90, 'xMax': 90}, data=self.pierside,
            tip='AngularDEC: {x:0.1f}\nErrorDec: {y:0.1f}\nPier: {data}'.format)
        return True

    def draw_scaleImage(self):
        """
        :return:    True if ok for testing
        """
        self.ui.scaleImage.p[0].setLabel('bottom', 'Star Number')
        self.ui.scaleImage.p[0].setLabel('left', 'Image Scale [arcsec/pix]')
        color = [self.M_GREEN if p == 'W' else self.M_YELLOW for p in self.pierside]
        self.ui.scaleImage.plot(
            self.index, self.scaleS, color=color, data=self.pierside,
            tip='PointNo: {x:0.0f}\nScale: {y:0.1f}\nPier: {data}'.format)
        return True

    def draw_errorAscending(self):
        """
        :return:    True if ok for testing
        """
        self.ui.errorAscending.p[0].setLabel('bottom', 'Starcount')
        self.ui.errorAscending.p[0].setLabel('left', 'Error per Star [arcsec]')
        temp = sorted(zip(self.errorRMS, self.pierside))
        y = [x[0] for x in temp]
        pierside = [x[1] for x in temp]
        color = [self.M_GREEN if p == 'W' else self.M_YELLOW for p in pierside]
        self.ui.errorAscending.plot(
            self.index, y, color=color, data=pierside,
            tip='ErrorRMS: {y:0.1f}\nPier: {data}'.format)
        return True

    def draw_modelPositions(self):
        """
        :return:    True if ok for testing
        """
        self.ui.modelPositions.barItem.setLabel('right', 'Error [RMS]')
        self.ui.modelPositions.plot(
            self.azimuth, self.altitude, z=self.errorRMS, ang=self.errorAngle,
            range={'xMin': -91, 'yMin': -91, 'xMax': 91, 'yMax': 91},
            bar=True, data=self.errorRMS, reverse=True,
            tip='ErrorRMS: {data:0.1f}'.format)
        self.ui.modelPositions.plotLoc(self.latitude)
        return True

    def draw_errorDistribution(self):
        """
        :return:    True if ok for testing
        """
        color = [self.M_GREEN if p == 'W' else self.M_YELLOW for p in self.pierside]
        self.ui.errorDistribution.plot(
            self.errorAngle, self.errorRMS, color=color, data=self.pierside,
            tip='ErrorRMS: {y:0.1f}\nPier: {data}'.format)
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
