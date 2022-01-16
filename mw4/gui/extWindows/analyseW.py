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
from PyQt5.QtWidgets import QApplication
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.colors import Normalize
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
        self.raRawErrors = self.embedMatplot(self.ui.raRawErrors)
        self.decRawErrors = self.embedMatplot(self.ui.decRawErrors)
        self.raErrors = self.embedMatplot(self.ui.raErrors)
        self.decErrors = self.embedMatplot(self.ui.decErrors)
        self.raRawErrorsRef = self.embedMatplot(self.ui.raRawErrorsRef)
        self.decRawErrorsRef = self.embedMatplot(self.ui.decRawErrorsRef)
        self.raErrorsRef = self.embedMatplot(self.ui.raErrorsRef)
        self.decErrorsRef = self.embedMatplot(self.ui.decErrorsRef)
        self.scaleImage = self.embedMatplot(self.ui.scaleImage)
        self.modelPositions = self.embedMatplot(self.ui.modelPositions)
        self.errorAscending = self.embedMatplot(self.ui.errorAscending)
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

    def plotFigureFlat(self, axe, x, y, p, xLabel, yLabel, sort=False, poly=0):
        """
        :param axe:
        :param x:
        :param y:
        :param p: pierside
        :param xLabel:
        :param yLabel:
        :param sort:
        :param poly:
        :return: True for test purpose
        """
        axe.set_xlabel(xLabel)
        axe.set_ylabel(yLabel)
        if sort:
            x, y, pierside = zip(*sorted(zip(x, y, p)))
        else:
            pierside = p

        if self.ui.winsorizedLimit.isChecked():
            y = winsorize(y, limits=0.03)

        xW = [x for x, y, p in zip(x, y, pierside) if p == 'W']
        yW = [y for x, y, p in zip(x, y, pierside) if p == 'W']
        xE = [x for x, y, p in zip(x, y, pierside) if p == 'E']
        yE = [y for x, y, p in zip(x, y, pierside) if p == 'E']

        if poly:
            try:
                polynomW = np.polyfit(xW, yW, poly)
            except Exception as e:
                self.log.debug(f'Interpolation failed: {e}')
            else:
                hasNoNan = not np.isnan(polynomW).any()
                hasNoInf = not np.isinf(polynomW).any()

                if hasNoNan and hasNoInf:
                    meanW = np.poly1d(polynomW)(xW)
                    axe.plot(xW, meanW, color=self.M_GREEN, alpha=0.4, lw=4)

            try:
                polynomE = np.polyfit(xE, yE, poly)
            except Exception as e:
                self.log.debug(f'Interpolation failed: {e}')
            else:
                hasNoNan = not np.isnan(polynomE).any()
                hasNoInf = not np.isinf(polynomE).any()

                if hasNoNan and hasNoInf:
                    meanE = np.poly1d(polynomE)(xE)
                    axe.plot(xE, meanE, color=self.M_YELLOW, alpha=0.4, lw=4)

        axe.plot(xW, yW, marker='.', markersize=7, linestyle='none',
                 color=self.M_GREEN)
        axe.plot(xE, yE, marker='.', markersize=7, linestyle='none',
                 color=self.M_YELLOW)
        axe.figure.canvas.draw()
        return True

    def scatterFigureFlat(self, axe, x, y, z, xLabel, yLabel):
        """
        :param axe:
        :param x:
        :param y:
        :param z:
        :param xLabel:
        :param yLabel:
        :return: True for test purpose
        """
        axe.set_xlabel(xLabel)
        axe.set_ylabel(yLabel)

        if self.ui.winsorizedLimit.isChecked():
            z = winsorize(z, limits=0.03)

        cm = plt.cm.get_cmap('RdYlGn_r')
        sMax = max(z)
        sMin = min(z)
        axe.scatter(x, y, c=z, vmin=sMin, vmax=sMax, cmap=cm)
        axe.figure.canvas.draw()
        return True

    def draw_raRawErrors(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.raRawErrors, horizon=True)
        x = self.azimuth
        y = self.altitude
        z = np.abs(self.errorRA_S)
        xLabel = 'Azimuth [deg]'
        yLabel = 'Altitude [deg]'
        self.scatterFigureFlat(axe, x, y, z, xLabel, yLabel)
        return True

    def draw_decRawErrors(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.decRawErrors, horizon=True)
        x = self.azimuth
        y = self.altitude
        z = np.abs(self.errorDEC_S)
        xLabel = 'Azimuth [deg]'
        yLabel = 'Altitude [deg]'
        self.scatterFigureFlat(axe, x, y, z, xLabel, yLabel)
        return True

    def draw_raErrors(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.raErrors, horizon=True)
        x = self.azimuth
        y = self.altitude
        z = np.abs(self.errorRA)
        xLabel = 'Azimuth [deg]'
        yLabel = 'Altitude [deg]'
        self.scatterFigureFlat(axe, x, y, z, xLabel, yLabel)
        return True

    def draw_decError(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.decErrors, horizon=True)
        x = self.azimuth
        y = self.altitude
        z = np.abs(self.errorDEC)
        xLabel = 'Azimuth [deg]'
        yLabel = 'Altitude [deg]'
        self.scatterFigureFlat(axe, x, y, z, xLabel, yLabel)
        return True

    def draw_raErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.raErrorsRef)
        x = self.angularPosRA
        y = self.errorRA
        p = self.pierside
        xLabel = 'RA Encoder Abs [deg]'
        yLabel = 'Error per Star [arcsec]'
        self.plotFigureFlat(axe, x, y, p, xLabel, yLabel, True, 3)
        return True

    def draw_decErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.decErrorsRef)
        x = self.angularPosDEC
        y = self.errorDEC
        p = self.pierside
        y = [x if p == 'W' else -x for x, p in zip(y, p)]
        xLabel = 'DEC Encoder Abs [deg]'
        yLabel = 'Error per Star [arcsec]'
        self.plotFigureFlat(axe, x, y, p, xLabel, yLabel, True, 3)
        return True

    def draw_raRawErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.raRawErrorsRef)
        x = self.angularPosRA
        y = self.errorRA_S
        p = self.pierside
        xLabel = 'RA Encoder Abs [deg]'
        yLabel = 'Error per Star [arcsec]'
        self.plotFigureFlat(axe, x, y, p, xLabel, yLabel, True, 3)
        return True

    def draw_decRawErrorsRef(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.decRawErrorsRef)
        x = self.angularPosDEC
        y = self.errorDEC_S
        p = self.pierside
        y = [y if p == 'W' else -y for y, p in zip(y, p)]
        xLabel = 'DEC Encoder Abs [deg]'
        yLabel = 'Error per Star [arcsec]'
        self.plotFigureFlat(axe, x, y, p, xLabel, yLabel, True, 3)
        return True

    def draw_scaleImage(self):
        """
        :return:    True if ok for testing
        """
        axe, _ = self.generateFlat(widget=self.scaleImage)
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.3f',))
        x = self.index
        y = self.scaleS
        p = self.pierside
        xLabel = 'Star Number'
        yLabel = 'Image Scale [arcsec/pix]'
        self.plotFigureFlat(axe, x, y, p, xLabel, yLabel, False, 3)
        return True

    def draw_errorAscending(self):
        """
        :return:    True if ok for testing
        """
        axe, fig = self.generateFlat(widget=self.errorAscending)
        xLabel = 'Star'
        yLabel = 'Error per Star [arcsec]'

        y = self.errorRMS
        pierside = self.pierside
        x = self.index

        temp = sorted(zip(y, pierside))
        y = [x[0] for x in temp]
        p = [x[1] for x in temp]

        self.plotFigureFlat(axe, x, y, p, xLabel, yLabel, False, 3)
        return True

    def draw_modelPositions(self):
        """
        showModelPosition draws a polar plot of the align model stars and their
        errors in color. the basic setup of the plot is taking place in the
        central widget class. which is instantiated from there. important: the
        coordinate in model is in HA and DEC  and not in RA and DEC. using
        skyfield is a little bit misleading, because you address the hour angle
        as .ra.hours

        the vectors displayed are derived from the spec of 10micron:
            ppp is the polar angle of the measured star with respect to the
            modeled star in the equatorial system in degrees from 0 to 359 (0
            towards the north pole, 90 towards east)

        :return:    True if ok for testing
        """
        axe, fig = self.generatePolar(widget=self.modelPositions)
        axe.set_ylim(0, 90)
        axe.set_yticklabels('')

        altitude = self.altitude
        azimuth = self.azimuth
        error = self.errorRMS
        ang = self.errorAngle

        cm = plt.cm.get_cmap('RdYlGn_r')
        sMax = max(error)
        sMin = min(error)
        az = azimuth / 180.0 * np.pi
        alt = 90 - altitude

        scatter = axe.scatter(az, alt, c=error, vmin=sMin, vmax=sMax, cmap=cm)

        norm = Normalize(vmin=sMin, vmax=sMax)
        sm = plt.cm.ScalarMappable(cmap=cm, norm=norm)
        sm.set_array([])

        fm = ticker.FormatStrFormatter('%1.0f')
        cb = plt.colorbar(sm, pad=0.1, fraction=0.12, aspect=25, shrink=0.9, format=fm)
        cb.set_label('Error [arcsec]', color=self.M_BLUE)
        yTicks = plt.getp(cb.ax.axes, 'yticklabels')
        plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        lat = self.latitude

        if lat is None:
            axe.figure.canvas.draw()
            return True

        npX = (90 - lat) * np.cos(np.radians(0 + 90))
        npY = (90 - lat) * np.sin(np.radians(0 + 90))

        axe.plot(0, 90 - lat, marker='o', markersize=10, color=self.M_BLUE, alpha=0.8,
                 zorder=-10)
        axe.plot(0, 90 - lat, marker='o', markersize=20, color=self.M_BLUE, alpha=0.8,
                 lw=10, fillstyle='none', zorder=-10)
        axe.plot(0, 90 - lat, marker='o', markersize=35, color=self.M_BLUE, alpha=0.8,
                 lw=10, fillstyle='none', zorder=-10)

        for alt, az, ang, err in zip(altitude, azimuth, ang, error):
            pX = (90 - alt) * np.cos(np.radians(az + 90))
            pY = (90 - alt) * np.sin(np.radians(az + 90))

            vec = np.arctan2(pY - npY, pX - npX) + np.radians(90) + np.radians(ang)

            x = az / 180.0 * np.pi
            y = 90 - alt
            u = np.sin(vec)
            v = np.cos(vec)

            col = cm((err - sMin) / sMax)

            axe.quiver(x, y, u, v,
                       color=col,
                       scale=17,
                       headlength=0,
                       headwidth=1,
                       alpha=0.8,
                       zorder=-10,
                       )

        self.generateColorbar(figure=fig, scatter=scatter, label='Error [arcsec]')
        axe.figure.canvas.draw()

        return True

    def draw_errorDistribution(self):
        """
        showErrorDistribution draws a polar plot of the align model stars and
        their errors in color. the basic setup of the plot is taking place in the
        central widget class. which is instantiated from there. important: the
        coordinate in model is in HA and DEC  and not in RA and DEC. using
        skyfield is a little bit misleading, because you address the hour angle
        as .ra.hours

        :return:    True if ok for testing
        """
        axe, fig = self.generatePolar(widget=self.errorDistribution)
        x = [val / 180.0 * np.pi for val in self.errorAngle]
        y = self.errorRMS

        for x, y, pierside in zip(x, y, self.pierside):
            if pierside == 'W':
                color = self.M_GREEN

            else:
                color = self.M_YELLOW

            axe.plot(x, y, marker='.', markersize=7, linestyle='none', color=color)
        axe.figure.canvas.draw()
        return True

    def drawAll(self):
        """
        :return:
        """
        for chart in self.charts:
            if self.closing:
                break
            chart()
            QApplication.processEvents()
        return True
