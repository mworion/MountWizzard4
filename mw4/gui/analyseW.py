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
import json
import os

# external packages
import PyQt5
import matplotlib.pyplot as plt
from matplotlib import ticker
import numpy as np
from scipy.stats.mstats import winsorize

# local import
from mw4.gui import widget
from mw4.gui.widgets import analyse_ui


class AnalyseWindow(widget.MWidget):
    """
    the analyse window class handles

    """

    __all__ = ['AnalyseWindow',
               ]

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.ui = analyse_ui.Ui_AnalyseDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.modelJSON = None
        self.wIcon(self.ui.load, PyQt5.QtGui.QIcon(':/icon/load.svg'))

        self.raPointErrors = self.embedMatplot(self.ui.raPointErrors,
                                               constrainedLayout=True)
        self.raPointErrors.parentWidget().setStyleSheet(self.BACK_BG)
        self.decPointErrors = self.embedMatplot(self.ui.decPointErrors,
                                                constrainedLayout=True)
        self.decPointErrors.parentWidget().setStyleSheet(self.BACK_BG)
        self.raModelErrors = self.embedMatplot(self.ui.raModelErrors,
                                               constrainedLayout=True)
        self.raModelErrors.parentWidget().setStyleSheet(self.BACK_BG)
        self.decModelErrors = self.embedMatplot(self.ui.decModelErrors,
                                                constrainedLayout=True)
        self.decModelErrors.parentWidget().setStyleSheet(self.BACK_BG)
        self.scaleImage = self.embedMatplot(self.ui.scaleImage,
                                            constrainedLayout=True)
        self.scaleImage.parentWidget().setStyleSheet(self.BACK_BG)
        self.modelPositions = self.embedMatplot(self.ui.modelPositions,
                                                constrainedLayout=True)
        self.modelPositions.parentWidget().setStyleSheet(self.BACK_BG)
        self.errorAscending = self.embedMatplot(self.ui.errorAscending,
                                                constrainedLayout=True)
        self.errorAscending.parentWidget().setStyleSheet(self.BACK_BG)
        self.errorDistribution = self.embedMatplot(self.ui.errorDistribution,
                                                   constrainedLayout=True)
        self.errorDistribution.parentWidget().setStyleSheet(self.BACK_BG)

        self.ui.load.clicked.connect(self.loadModel)
        self.ui.winsorizedLimit.clicked.connect(self.drawAll)
        self.ui.limit.valueChanged.connect(self.drawAll)

        self.initConfig()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        if 'analyseW' not in self.app.config:
            self.app.config['analyseW'] = {}
        config = self.app.config['analyseW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        self.ui.winsorizedLimit.setChecked(config.get('winsorizedLimit', False))
        self.ui.limit.setValue(config.get('limit', 3))

        self.showWindow()

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        if 'analyseW' not in self.app.config:
            self.app.config['analyseW'] = {}
        config = self.app.config['analyseW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['winsorizedLimit'] = self.ui.winsorizedLimit.isChecked()
        config['limit'] = self.ui.limit.value()

        return True

    def closeEvent(self, closeEvent):
        """
        closeEvent is overloaded to be able to store the data before the windows is close
        and all it's data is garbage collected

        :param closeEvent:
        :return:
        """
        self.storeConfig()

        # gui signals
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        showWindow starts constructing the main window for satellite view and shows the
        window content

        :return: True for test purpose
        """
        self.show()

        return True

    def convertModelData(self):
        """

        :return: True for test purpose
        """

        return True

    def loadModel(self):
        """
        loadModel selects one or more models from the files system

        :return: success
        """

        folder = self.app.mwGlob['modelDir']
        loadFilePath, fileName, ext = self.openFile(self,
                                                    'Open model file',
                                                    folder,
                                                    'Model files (*.model)',
                                                    multiple=False,
                                                    )
        if not loadFilePath:
            return False

        with open(loadFilePath, 'r') as infile:
            modelJSON = json.load(infile)

        self.ui.filename.setText(os.path.basename(loadFilePath))
        self.ui.eposure.setText(f'{modelJSON[0]["exposureTime"]}')
        self.ui.solver.setText(modelJSON[0]['astrometryApp'])
        self.ui.binning.setText(f'{modelJSON[0]["binning"]:1.0f}')
        self.ui.time.setText(modelJSON[0]['julianDate'])
        self.ui.subframe.setText(f'{modelJSON[0]["subFrame"]:3.0f}')
        self.ui.flipped.setText(str(modelJSON[0]['flippedS']))

        self.convertModelData()

        if 'polarError' in modelJSON[0]:
            self.ui.polarError.setText(f'{modelJSON[0]["polarError"]:5.1f}')
        if 'modelTerms' in modelJSON[0]:
            self.ui.modelTerms.setText(f'{modelJSON[0]["modelTerms"]:02.0f}')
        if 'modelErrorRMS' in modelJSON[0]:
            self.ui.modelErrorRMS.setText(f'{modelJSON[0]["modelErrorRMS"]:5.1f}')
        if 'modelOrthoError' in modelJSON[0]:
            self.ui.modelOrthoError.setText(f'{modelJSON[0]["modelOrthoError"]:5.1f}')
        if 'modelPolarError' in modelJSON[0]:
            self.ui.modelPolarError.setText(f'{modelJSON[0]["modelPolarError"]:5.1f}')
        if 'version' in modelJSON[0]:
            version = modelJSON[0]["version"].lstrip('MountWizzard4 - v')
            self.ui.version.setText(f'{version}')
        if 'focalLength' in modelJSON[0]:
            self.ui.focalLength.setText(f'{modelJSON[0]["focalLength"]:4.0f}')
        if 'profile' in modelJSON[0]:
            self.ui.profile.setText(f'{modelJSON[0]["profile"]}')
        if 'firmware' in modelJSON[0]:
            self.ui.firmware.setText(f'{modelJSON[0]["firmware"]}')

        self.modelJSON = modelJSON
        self.drawAll()

        return True

    def draw_raPointErrors(self, model):
        """
        draw_raPointErrors draws a plot of

        :param model:
        :return:    True if ok for testing
        """

        axe, fig = self.generateFlat(widget=self.raPointErrors)

        axe.set_xlabel('Star',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Error per Star [RMS]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        errors = model['errorRA_S']

        if self.ui.winsorizedLimit.isChecked():
            errors = winsorize(errors, limits=self.ui.limit.value() / 100)

        index = range(0, len(errors))

        for x, y, pierside in zip(index, errors, model['pierside']):
            if pierside == 'W':
                color = self.M_GREEN
            else:
                color = self.M_YELLOW
            axe.plot(x,
                     y,
                     marker='.',
                     markersize=5,
                     linestyle='none',
                     color=color)

        axe.figure.canvas.draw()

        return True

    def draw_decPointErrors(self, model):
        """
        draw_raPointErrors draws a plot of

        :param model:
        :return:    True if ok for testing
        """

        axe, fig = self.generateFlat(widget=self.decPointErrors)

        axe.set_xlabel('Star',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Error per Star [RMS]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        errors = model['errorDEC_S']

        if self.ui.winsorizedLimit.isChecked():
            errors = winsorize(errors, limits=self.ui.limit.value() / 100)

        index = range(0, len(errors))

        for x, y, pierside in zip(index, errors, model['pierside']):
            if pierside == 'W':
                color = self.M_GREEN
            else:
                color = self.M_YELLOW
            axe.plot(x,
                     y,
                     marker='.',
                     markersize=5,
                     linestyle='none',
                     color=color)

        axe.figure.canvas.draw()

        return True

    def draw_raModelErrors(self, model):
        """
        draw_raPointErrors draws a plot of

        :param model:
        :return:    True if ok for testing
        """

        axe, fig = self.generateFlat(widget=self.raModelErrors)

        axe.set_xlabel('Star',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Error per Star [RMS]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        errors = model['errorRA']

        if self.ui.winsorizedLimit.isChecked():
            errors = winsorize(errors, limits=self.ui.limit.value() / 100)

        index = range(0, len(errors))

        for x, y, pierside in zip(index, errors, model['pierside']):
            if pierside == 'W':
                color = self.M_GREEN
            else:
                color = self.M_YELLOW
            axe.plot(x,
                     y,
                     marker='.',
                     markersize=5,
                     linestyle='none',
                     color=color)

        axe.figure.canvas.draw()

        return True

    def draw_decModelErrors(self, model):
        """
        draw_raPointErrors draws a plot of

        :param model:
        :return:    True if ok for testing
        """

        axe, fig = self.generateFlat(widget=self.decModelErrors)

        axe.set_xlabel('Star',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Error per Star [RMS]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        errors = model['errorDEC']

        if self.ui.winsorizedLimit.isChecked():
            errors = winsorize(errors, limits=self.ui.limit.value() / 100)

        index = range(0, len(errors))

        for x, y, pierside in zip(index, errors, model['pierside']):
            if pierside == 'W':
                color = self.M_GREEN
            else:
                color = self.M_YELLOW
            axe.plot(x,
                     y,
                     marker='.',
                     markersize=5,
                     linestyle='none',
                     color=color)

        axe.figure.canvas.draw()

        return True

    def draw_scaleImage(self, model):
        """
        draw_raPointErrors draws a plot of

        :param model:
        :return:    True if ok for testing
        """

        axe, fig = self.generateFlat(widget=self.scaleImage)
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.3f',))

        axe.set_xlabel('Star',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Image Scale [arcsec/pix]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        errors = model['scaleS']

        if self.ui.winsorizedLimit.isChecked():
            errors = winsorize(errors, limits=self.ui.limit.value() / 100)

        index = range(0, len(errors))

        for x, y, pierside in zip(index, errors, model['pierside']):
            if pierside == 'W':
                color = self.M_GREEN
            else:
                color = self.M_YELLOW
            axe.plot(x,
                     y,
                     marker='.',
                     markersize=5,
                     linestyle='none',
                     color=color)

        axe.figure.canvas.draw()

        return True

    def draw_modelPositions(self, model):
        """
        showModelPosition draws a polar plot of the align model stars and their errors in
        color. the basic setup of the plot is taking place in the central widget class.
        which is instantiated from there. important: the coordinate in model is in HA and
        DEC  and not in RA and DEC. using skyfield is a little bit misleading, because you
        address the hour angle as .ra.hours

        :param model:
        :return:    True if ok for testing
        """

        axe, fig = self.generatePolar(widget=self.modelPositions)

        axe.set_yticks(range(0, 90, 10))
        axe.set_ylim(0, 90)
        yLabel = ['', '', '', '', '', '', '', '', '']
        axe.set_yticklabels(yLabel)

        altitude = np.asarray(model['altitude'])
        azimuth = np.asarray(model['azimuth'])
        error = np.asarray(model['errorRMS'])

        # and plot it
        cm = plt.cm.get_cmap('RdYlGn_r')
        colors = np.asarray(error)
        scaleErrorMax = max(colors)
        scaleErrorMin = min(colors)
        area = [100 if x >= max(colors) else 30 for x in error]
        theta = azimuth / 180.0 * np.pi
        r = 90 - altitude
        scatter = axe.scatter(theta,
                              r,
                              c=colors,
                              vmin=scaleErrorMin,
                              vmax=scaleErrorMax,
                              s=area,
                              cmap=cm,
                              zorder=0,
                              )

        formatString = ticker.FormatStrFormatter('%1.0f')
        colorbar = fig.colorbar(scatter,
                                pad=0.1,
                                fraction=0.12,
                                aspect=25,
                                shrink=0.9,
                                format=formatString,
                                )
        colorbar.set_label('Error [arcsec]', color=self.M_BLUE)
        yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
        plt.setp(yTicks,
                 color=self.M_BLUE,
                 fontweight='bold')

        axe.figure.canvas.draw()
        return True

    def draw_errorAscending(self, model):
        """
        showErrorAscending draws a plot of the align model stars and their errors in ascending
        order.

        :param model:
        :return:    True if ok for testing
        """

        axe, fig = self.generateFlat(widget=self.errorAscending)

        axe.set_xlabel('Star',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Error per Star [RMS]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        errors = model['errorRMS']

        errors, pierside = zip(*sorted(zip(errors, model['pierside'])))

        if self.ui.winsorizedLimit.isChecked():
            errors = winsorize(errors, limits=self.ui.limit.value() / 100)

        index = range(0, len(errors))

        for x, y, pier in zip(index, errors, pierside):
            if pier == 'W':
                color = self.M_GREEN
            else:
                color = self.M_YELLOW
            axe.plot(x,
                     y,
                     marker='.',
                     markersize=5,
                     linestyle='none',
                     color=color)

        axe.figure.canvas.draw()

        return True

    def draw_errorDistribution(self, model):
        """
        showErrorDistribution draws a polar plot of the align model stars and their errors in
        color. the basic setup of the plot is taking place in the central widget class.
        which is instantiated from there. important: the coordinate in model is in HA and
        DEC  and not in RA and DEC. using skyfield is a little bit misleading, because you
        address the hour angle as .ra.hours

        :param model:
        :return:    True if ok for testing
        """

        if 'errorAngle' not in model:
            return False

        axe, fig = self.generatePolar(widget=self.errorDistribution)

        angles = [val / 180.0 * np.pi for val in model['errorAngle']]

        errors = model['errorRMS']

        for x, y, pierside in zip(angles, errors, model['pierside']):
            if pierside == 'W':
                color = self.M_GREEN
            else:
                color = self.M_YELLOW
            axe.plot(x,
                     y,
                     marker='.',
                     markersize=5,
                     linestyle='none',
                     color=color)

        axe.figure.canvas.draw()

        return True

    def drawAll(self):
        """

        :return: true for test purpose
        """

        if not self.modelJSON:
            return False

        self.ui.limit.setEnabled(False)
        model = dict()

        for key in self.modelJSON[0].keys():
            model[key] = list()
            for index in range(0, len(self.modelJSON)):
                model[key].append(self.modelJSON[index][key])

        self.draw_raPointErrors(model)
        self.draw_decPointErrors(model)
        self.draw_raModelErrors(model)
        self.draw_decModelErrors(model)
        self.draw_scaleImage(model)
        self.draw_modelPositions(model)
        self.draw_errorAscending(model)
        self.draw_errorDistribution(model)
        self.ui.limit.setEnabled(True)

        return True
