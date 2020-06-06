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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import glob
import json

# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
import numpy as np
import matplotlib.pyplot
from mountcontrol import convert

# local import


class ManageModel(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

        self.runningOptimize = False
        self.fittedModelFound = False

        ms = self.app.mount.signals
        ms.alignDone.connect(self.showModelPosition)
        ms.alignDone.connect(self.showErrorAscending)
        ms.alignDone.connect(self.showErrorDistribution)
        ms.namesDone.connect(self.setNameList)

        self.ui.checkShowErrorValues.stateChanged.connect(self.refreshModel)
        self.ui.refreshName.clicked.connect(self.refreshName)
        self.ui.refreshModel.clicked.connect(self.refreshModel)
        self.ui.clearModel.clicked.connect(self.clearModel)
        self.ui.loadName.clicked.connect(self.loadName)
        self.ui.saveName.clicked.connect(self.saveName)
        self.ui.deleteName.clicked.connect(self.deleteName)
        self.ui.runOptimize.clicked.connect(self.runOptimize)
        self.ui.cancelOptimize.clicked.connect(self.cancelOptimize)
        self.ui.deleteWorstPoint.clicked.connect(self.deleteWorstPoint)
        # self.ui.test.clicked.connect(self.findFittingModel)

        model = self.app.mount.model
        self.ui.targetRMS.valueChanged.connect(lambda: self.showModelPosition(model))
        self.ui.targetRMS.valueChanged.connect(lambda: self.showErrorAscending(model))
        self.ui.targetRMS.valueChanged.connect(lambda: self.showErrorDistribution(model))

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.checkShowErrorValues.setChecked(config.get('checkShowErrorValues', False))
        self.ui.targetRMS.setValue(config.get('targetRMS', 99))
        self.ui.optimizeOverall.setChecked(config.get('optimizeOverall', True))
        self.ui.optimizeSingle.setChecked(config.get('optimizeSingle', True))
        self.showModelPosition(None)
        self.showErrorAscending(None)
        self.showErrorDistribution(None)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['checkShowErrorValues'] = self.ui.checkShowErrorValues.isChecked()
        config['targetRMS'] = self.ui.targetRMS.value()
        config['optimizeOverall'] = self.ui.optimizeOverall.isChecked()
        config['optimizeSingle'] = self.ui.optimizeSingle.isChecked()
        return True

    def setNameList(self, model):
        """
        setNameList populates the list of model names in the main window. before adding the
        data, the existent list will be deleted.

        :return:    True if ok for testing
        """

        self.ui.nameList.clear()
        for name in model.nameList:
            self.ui.nameList.addItem(name)
        self.ui.nameList.sortItems()
        self.ui.nameList.update()
        return True

    def findValue(self, buildStar, mountModel):
        """

        :param buildStar:
        :param mountModel:
        :return: success
        """

        for mountStar in mountModel.starList:
            val1 = buildStar['errorDEC']
            val2 = mountStar.errorDEC()
            if not val1 or not val2:
                continue
            if abs(val1 - val2) > 0.0001:
                continue
            # print(val1, val2, abs(val1 - val2))
            val1 = buildStar['errorRA']
            val2 = mountStar.errorRA()
            if not val1 or not val2:
                continue
            if abs(val1 - val2) > 0.0001:
                continue
            # print(val1, val2, abs(val1 - val2))
            # print(buildStar['errorRMS'], mountStar.errorRMS)
            return True

        return False

    def findFittingModel(self):
        """
        findFittingModel takes the actual loaded model from the mount and tries to find
        the fitting model run data. therefore it compares up to 5 points to find out.

        :return: success
        """

        return False

        mountModel = self.app.mount.model
        modelFileList = glob.glob(self.app.mwGlob['modelDir'] + '/*.model')

        found = False
        for modelFile in modelFileList:
            # print(modelFile)
            with open(modelFile, 'r') as inFile:
                buildModelData = json.load(inFile)
                for buildStar in buildModelData:
                    suc = self.findValue(buildStar, mountModel)
                    if suc:
                        pass
                        # print(modelFile)
        return True

    def generatePolar(self, widget=None, title=''):
        """

        :param widget:
        :param title:
        :return:
        """

        if widget is None:
            return None, None
        if not hasattr(widget, 'figure'):
            return None, None

        fig = widget.figure
        fig.clf()
        axe = fig.add_subplot(1,
                              1,
                              1,
                              polar=True,
                              facecolor=self.M_GREY_DARK)
        axe.grid(True,
                 color=self.M_GREY,
                 )
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      pad=15,
                      )
        axe.tick_params(axis='x',
                        colors=self.M_BLUE,
                        labelsize=12,
                        )
        axe.tick_params(axis='y',
                        colors=self.M_BLUE,
                        labelsize=12,
                        )
        axe.set_theta_zero_location('N')
        axe.set_rlabel_position(45)
        axe.set_theta_direction(-1)
        xLabel = ['0-N', '45-NE', '90-E', '135-SE', '180-S', '215-SW', '270-W', '315-NW']
        axe.set_xticklabels(xLabel)

        return axe, fig

    def showModelPosition(self, model):
        """
        showModelPosition draws a polar plot of the align model stars and their errors in
        color. the basic setup of the plot is taking place in the central widget class.
        which is instantiated from there. important: the coordinate in model is in HA and
        DEC  and not in RA and DEC. using skyfield is a little bit misleading, because you
        address the hour angle as .ra.hours

        :return:    True if ok for testing
        """

        # check entry conditions for displaying a polar plot
        if model is None:
            hasNoStars = True
        elif not hasattr(model, 'starList'):
            hasNoStars = True
        else:
            hasNoStars = model.starList is None or not model.starList

        axe, fig = self.generatePolar(widget=self.modelPositionPlot,
                                      title='Actual Mount Model')

        axe.set_yticks(range(0, 90, 10))
        axe.set_ylim(0, 90)
        yLabel = ['', '', '', '', '', '', '', '', '', '']
        axe.set_yticklabels(yLabel)

        if hasNoStars:
            axe.figure.canvas.draw()
            return False

        # start with plotting
        lat = self.app.config.get('topoLat', 51.47)

        altitude = []
        azimuth = []
        error = []
        for star in model.starList:
            alt, az = convert.topoToAltAz(star.coord.ra.hours,
                                          star.coord.dec.degrees,
                                          lat)
            altitude.append(alt)
            azimuth.append(az)
            error.append(star.errorRMS)
        altitude = np.asarray(altitude)
        azimuth = np.asarray(azimuth)
        error = np.asarray(error)

        # and plot it
        cm = matplotlib.pyplot.cm.get_cmap('RdYlGn_r')
        colors = np.asarray(error)
        scaleErrorMax = max(colors)
        scaleErrorMin = min(colors)
        area = [200 if x >= max(colors) else 60 for x in error]
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
        if self.ui.checkShowErrorValues.isChecked():
            for star in model.starList:
                text = '{0:3.1f}'.format(star.errorRMS)
                axe.annotate(text,
                             xy=(theta[star.number - 1],
                                 r[star.number - 1]),
                             color=self.M_BLUE,
                             fontsize=9,
                             fontweight='bold',
                             zorder=1,
                             )
        formatString = matplotlib.ticker.FormatStrFormatter('%1.0f')
        colorbar = fig.colorbar(scatter,
                                pad=0.1,
                                fraction=0.12,
                                aspect=25,
                                shrink=0.9,
                                format=formatString,
                                )
        colorbar.set_label('Error [arcsec]', color=self.M_BLUE)
        yTicks = matplotlib.pyplot.getp(colorbar.ax.axes, 'yticklabels')
        matplotlib.pyplot.setp(yTicks,
                               color=self.M_BLUE,
                               fontweight='bold')
        yValues = self.ui.targetRMS.value()
        xMin = colorbar.ax.get_xlim()[0]
        xMax = colorbar.ax.get_xlim()[1]
        vRange = xMax - xMin
        xValues = [xMin - 0.15 * vRange, xMax + 0.2 * vRange]
        colorbar.ax.plot(xValues, [yValues] * 2, self.M_PINK_H, lw=3, clip_on=False)

        axe.figure.canvas.draw()
        return True

    def showErrorAscending(self, model):
        """
        showErrorAscending draws a plot of the align model stars and their errors in ascending
        order.

        :return:    True if ok for testing
        """

        # check entry conditions for displaying a polar plot
        if model is None:
            hasNoStars = True
        elif not hasattr(model, 'starList'):
            hasNoStars = True
        else:
            hasNoStars = model.starList is None or not model.starList

        figure = self.errorAscendingPlot.figure
        figure.clf()
        axe = figure.add_subplot(1, 1, 1, facecolor=self.M_GREY_DARK)

        if hasNoStars:
            axe.figure.canvas.draw()
            return False

        axe.set_title('Model Point Errors in ascending order',
                      color=self.M_BLUE,
                      fontweight='bold',
                      pad=15,
                      )
        axe.spines['bottom'].set_color(self.M_BLUE)
        axe.spines['top'].set_color(self.M_BLUE)
        axe.spines['left'].set_color(self.M_BLUE)
        axe.spines['right'].set_color(self.M_BLUE)
        axe.grid(True, color=self.M_GREY)
        axe.tick_params(axis='x',
                        colors=self.M_BLUE,
                        labelsize=12)
        axe.tick_params(axis='y',
                        colors=self.M_BLUE,
                        labelsize=12)
        axe.set_xlabel('Star',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Error per Star [RMS]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        errors = [star.errorRMS for star in model.starList]
        errors.sort()
        index = range(0, len(errors))
        axe.plot(index,
                 errors,
                 marker='.',
                 markersize=5,
                 linestyle='none',
                 color=self.M_GREEN)

        value = self.ui.targetRMS.value()
        axe.plot([0, len(index) - 1],
                 [value, value],
                 lw=3,
                 color=self.M_PINK_H)

        axe.figure.canvas.draw()

        return True

    def showErrorDistribution(self, model):
        """
        showErrorDistribution draws a polar plot of the align model stars and their errors in
        color. the basic setup of the plot is taking place in the central widget class.
        which is instantiated from there. important: the coordinate in model is in HA and
        DEC  and not in RA and DEC. using skyfield is a little bit misleading, because you
        address the hour angle as .ra.hours

        :return:    True if ok for testing
        """

        # check entry conditions for displaying a polar plot
        if model is None:
            hasNoStars = True
        elif not hasattr(model, 'starList'):
            hasNoStars = True
        else:
            hasNoStars = model.starList is None or not model.starList

        axe, fig = self.generatePolar(widget=self.errorDistributionPlot,
                                      title='Error Distribution')

        if hasNoStars:
            axe.figure.canvas.draw()
            return False

        angles = [star.errorAngle.degrees / 180.0 * np.pi for star in model.starList]
        errors = [star.errorRMS for star in model.starList]

        axe.plot(angles,
                 errors,
                 marker='.',
                 markersize=5,
                 linestyle='none',
                 color=self.M_GREEN)

        values = [self.ui.targetRMS.value()] * 73
        angles = np.arange(0, 365 / 180.0 * np.pi, 5 / 180.0 * np.pi)
        axe.plot(angles,
                 values,
                 lw=3,
                 color=self.M_PINK_H)

        axe.figure.canvas.draw()

        return True

    def clearRefreshName(self):
        """
        clearRefreshName is the buddy function for refreshName

        :return: True for test purpose
        """

        self.changeStyleDynamic(self.ui.refreshName, 'running', 'false')
        self.ui.deleteName.setEnabled(True)
        self.ui.saveName.setEnabled(True)
        self.ui.loadName.setEnabled(True)
        self.app.mount.signals.namesDone.disconnect(self.clearRefreshName)
        self.app.message.emit('Model names refreshed', 0)
        return True

    def refreshName(self):
        """
        refreshName disables interfering functions in gui and start reloading the
        names list for model in the mount computer. it connects a link to clearRefreshNames
        which enables the former disabled gui buttons and removes the link to the method.
        after it triggers the refresh of names, it finished, because behaviour is event
        driven

        :return: True for test purpose
        """

        self.app.mount.signals.namesDone.connect(self.clearRefreshName)
        self.ui.deleteName.setEnabled(False)
        self.ui.saveName.setEnabled(False)
        self.ui.loadName.setEnabled(False)
        self.changeStyleDynamic(self.ui.refreshName, 'running', 'true')
        self.app.mount.getNames()
        return True

    def loadName(self):
        """
        loadName take the given name and loads the stored model as the actual alignment
        model for the mount. after that it refreshes the alignment model data in
        mountwizzard

        :return: success
        """

        if self.ui.nameList.currentItem() is None:
            self.app.message.emit('No model name selected', 2)
            return False
        modelName = self.ui.nameList.currentItem().text()
        suc = self.app.mount.model.loadName(modelName)
        if not suc:
            self.app.message.emit('Model [{0}] cannot be loaded'.format(modelName), 2)
            return False
        else:
            self.app.message.emit('Model [{0}] loaded'.format(modelName), 0)
            self.refreshModel()
            return True

    def saveName(self):
        """
        saveName take the given name and saves the actual alignment model to the model
        database in the mount computer. after that it refreshes the list of the alignment
        model names in mountwizzard.

        :return: success
        """

        dlg = PyQt5.QtWidgets.QInputDialog()
        modelName, ok = dlg.getText(self,
                                    'Save model',
                                    'New model name',
                                    PyQt5.QtWidgets.QLineEdit.Normal,
                                    '',
                                    )
        if modelName is None or not modelName:
            self.app.message.emit('No model name given', 2)
            return False
        if not ok:
            return False
        suc = self.app.mount.model.storeName(modelName)
        if not suc:
            self.app.message.emit('Model [{0}] cannot be saved'.format(modelName), 2)
            return False
        else:
            self.app.message.emit('Model [{0}] saved'.format(modelName), 0)
            self.refreshName()
            return True

    def deleteName(self):
        """
        deleteName take the given name and deletes it from the model database in the
        mount computer. after that it refreshes the list of the alignment model names in
        mountwizzard.

        :return: success
        """

        if self.ui.nameList.currentItem() is None:
            self.app.message.emit('No model name selected', 2)
            return False
        modelName = self.ui.nameList.currentItem().text()
        msg = PyQt5.QtWidgets.QMessageBox
        reply = msg.question(self,
                             'Delete model',
                             'Delete model from database?',
                             msg.Yes | msg.No,
                             msg.No,
                             )
        if reply != msg.Yes:
            return False
        suc = self.app.mount.model.deleteName(modelName)
        if not suc:
            self.app.message.emit('Model [{0}] cannot be deleted'.format(modelName), 2)
            return False
        else:
            self.app.message.emit('Model [{0}] deleted'.format(modelName), 0)
            self.refreshName()
            return True

    def clearRefreshModel(self):
        """
        clearRefreshModel is the buddy function for refreshModel

        :return: True for test purpose
        """

        self.changeStyleDynamic(self.ui.refreshModel, 'running', 'false')
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.runOptimize.setEnabled(True)
        self.ui.cancelOptimize.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.app.mount.signals.alignDone.disconnect(self.clearRefreshModel)
        self.app.message.emit('Align model data refreshed', 0)
        suc = self.findFittingModel()
        if suc:
            self.app.message.emit('Stored model run found', 0)

        return True

    def refreshModel(self):
        """
        refreshModel disables interfering functions in gui and start reloading the
        alignment model from the mount computer. it connects a link to clearRefreshModel
        which enables the former disabled gui buttons and removes the link to the method.
        after it triggers the refresh of names, it finished, because behaviour is event
        driven

        :return: True for test purpose
        """

        self.changeStyleDynamic(self.ui.refreshModel, 'running', 'true')
        self.app.mount.signals.alignDone.connect(self.clearRefreshModel)
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.runOptimize.setEnabled(False)
        self.ui.cancelOptimize.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.app.mount.getAlign()

        return True

    def clearModel(self):
        """
        clearModel removes the actual alignment model.

        :return:
        """

        msg = PyQt5.QtWidgets.QMessageBox
        reply = msg.question(self,
                             'Clear model',
                             'Clear actual alignment model?',
                             msg.Yes | msg.No,
                             msg.No,
                             )
        if reply == msg.No:
            return False
        suc = self.app.mount.model.clearAlign()
        if not suc:
            self.app.message.emit('Actual model cannot be cleared', 2)
            return False
        else:
            self.app.message.emit('Actual model cleared', 0)
            self.refreshModel()
            return True

    def deleteWorstPoint(self):
        """
        deleteWorstPoint selects from the actual model stored in the mount the highest
        value of error, get it's index and deletes the point. afterward it refreshes the
        gui

        :return:
        """

        model = self.app.mount.model
        wIndex = model.starList.index(max(model.starList))
        wStar = model.starList[wIndex]

        suc = model.deletePoint(wStar.number)

        if not suc:
            self.app.message.emit('Worst point cannot be deleted', 2)
            return False
        else:
            self.app.message.emit('Worst point deleted', 0)
            self.refreshModel()
            return True

    def runTargetRMS(self):
        """
        runTargetRMS is the buddy function for runTargetRMS

        :return: True for test purpose
        """

        mount = self.app.mount
        if mount.model.errorRMS < self.ui.targetRMS.value():
            self.runningOptimize = False

        if mount.model.numberStars is None:
            numberStars = 0
        else:
            numberStars = mount.model.numberStars

        if self.runningOptimize and numberStars > 1:
            wIndex = mount.model.starList.index(max(mount.model.starList))
            wStar = mount.model.starList[wIndex]
            suc = mount.model.deletePoint(wStar.number)

            if not suc:
                self.runningOptimize = False
                self.app.message.emit(f'Star [{wStar.number}] cannot be deleted', 2)
            else:
                text = f'Star [{wStar.number:02d}]: RMS of [{wStar.errorRMS:04.1f}] deleted'
                self.app.message.emit(text, 0)
            mount.getAlign()
        else:
            self.finishOptimize()

        return True

    def runSingleRMS(self):
        """

        :return: True for test purpose
        """

        mount = self.app.mount
        if all([star.errorRMS < self.ui.targetRMS.value() for star in mount.model.starList]):
            self.runningOptimize = False

        if mount.model.numberStars is None:
            numberStars = 0
        else:
            numberStars = mount.model.numberStars

        if self.runningOptimize and numberStars > 1:
            wIndex = mount.model.starList.index(max(mount.model.starList))
            wStar = mount.model.starList[wIndex]
            suc = mount.model.deletePoint(wStar.number)

            if not suc:
                self.runningOptimize = False
                self.app.message.emit(f'Star [{wStar.number}] cannot be deleted', 2)
            else:
                text = f'Star [{wStar.number:02d}]: RMS of [{wStar.errorRMS:04.1f}] deleted'
                self.app.message.emit(text, 0)
            mount.getAlign()
        else:
            self.finishOptimize()

        return True

    def runOptimize(self):
        """
        runOptimize dispatches the optimization method. depending which method was
        chosen i the gui, the appropriate method is called

        :return: true for test purpose
        """

        self.app.message.emit('Start optimizing model', 0)
        self.runningOptimize = True
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.ui.refreshModel.setEnabled(False)
        self.changeStyleDynamic(self.ui.runOptimize, 'running', 'true')
        self.changeStyleDynamic(self.ui.cancelOptimize, 'cancel', 'true')

        if self.ui.optimizeOverall.isChecked():
            self.app.mount.signals.alignDone.connect(self.runTargetRMS)
            self.runTargetRMS()
        else:
            self.app.mount.signals.alignDone.connect(self.runSingleRMS)
            self.runSingleRMS()

        return True

    def finishOptimize(self):
        """

        :return:
        """

        if self.ui.optimizeOverall.isChecked():
            self.app.mount.signals.alignDone.disconnect(self.runTargetRMS)
        else:
            self.app.mount.signals.alignDone.disconnect(self.runSingleRMS)

        self.changeStyleDynamic(self.ui.runOptimize, 'running', 'false')
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.ui.refreshModel.setEnabled(True)
        self.changeStyleDynamic(self.ui.cancelOptimize, 'cancel', 'false')
        self.app.message.emit('Optimizing done', 0)

        return True

    def cancelOptimize(self):
        """
        cancelOptimize dispatches the optimization method. depending which method was
        chosen i the gui, the appropriate method is called

        :return: true for test purpose
        """

        self.runningOptimize = False

        return True
