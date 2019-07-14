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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
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

    def __init__(self):
        self.runningTargetRMS = False
        ms = self.app.mount.signals
        ms.alignDone.connect(self.showModelPolar)
        ms.namesDone.connect(self.setNameList)

        self.ui.checkShowErrorValues.stateChanged.connect(self.showModelPolar)
        self.ui.refreshName.clicked.connect(self.refreshName)
        self.ui.refreshModel.clicked.connect(self.refreshModel)
        self.ui.clearModel.clicked.connect(self.clearModel)
        self.ui.loadName.clicked.connect(self.loadName)
        self.ui.saveName.clicked.connect(self.saveName)
        self.ui.deleteName.clicked.connect(self.deleteName)
        self.ui.runTargetRMS.clicked.connect(self.runTargetRMS)
        self.ui.cancelTargetRMS.clicked.connect(self.cancelTargetRMS)
        self.ui.deleteWorstPoint.clicked.connect(self.deleteWorstPoint)

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
        self.showModelPolar(None)
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
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        self.wIcon(self.ui.runTargetRMS, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelTargetRMS, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.loadName, PyQt5.QtWidgets.QStyle.SP_DirOpenIcon)
        self.wIcon(self.ui.saveName, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.deleteName, PyQt5.QtWidgets.QStyle.SP_TrashIcon)
        self.wIcon(self.ui.refreshName, PyQt5.QtWidgets.QStyle.SP_BrowserReload)
        self.wIcon(self.ui.refreshModel, PyQt5.QtWidgets.QStyle.SP_BrowserReload)
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

    def showModelPolar(self, model):
        """
        showModelPolar draws a polar plot of the align model stars and their errors in
        color. the basic setup of the plot is taking place in the central widget class.
        which is instantiated from there.

        :return:    True if ok for testing
        """

        # check entry conditions for displaying a polar plot
        if model is None:
            hasNoStars = True
        elif not hasattr(model, 'starList'):
            hasNoStars = True
        else:
            hasNoStars = model.starList is None or not model.starList

        if hasNoStars:
            # clear the plot and return
            fig, axes = self.clearPolar(self.polarPlot)
            fig.subplots_adjust(left=0.1,
                                right=0.9,
                                bottom=0.1,
                                top=0.85,
                                )
            axes.figure.canvas.draw()
            return False

        # start with plotting
        fig, axes = self.clearPolar(self.polarPlot)
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
        scatter = axes.scatter(theta,
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
                axes.annotate(text,
                              xy=(theta[star.number - 1],
                                  r[star.number - 1]),
                              color='#2090C0',
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
        colorbar.set_label('Error [arcsec]', color='white')
        yTicks = matplotlib.pyplot.getp(colorbar.ax.axes, 'yticklabels')
        matplotlib.pyplot.setp(yTicks,
                               color='#2090C0',
                               fontweight='bold')
        axes.set_rmax(90)
        axes.set_rmin(0)
        axes.figure.canvas.draw()
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
        self.ui.runTargetRMS.setEnabled(True)
        self.ui.cancelTargetRMS.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.app.mount.signals.alignDone.disconnect(self.clearRefreshModel)
        self.app.message.emit('Align model data refreshed', 0)
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
        self.ui.runTargetRMS.setEnabled(False)
        self.ui.cancelTargetRMS.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.app.mount.getAlign()

        return True

    def clearRunTargetRMS(self):
        """
        clearRunTargetRMS is the buddy function for runTargetRMS

        :return: True for test purpose
        """

        mount = self.app.mount
        if mount.model.errorRMS < self.ui.targetRMS.value():
            self.runningTargetRMS = False

        if self.runningTargetRMS:
            wIndex = mount.model.starList.index(max(mount.model.starList))
            wStar = mount.model.starList[wIndex]
            suc = mount.model.deletePoint(wStar.number)
            if not suc:
                self.runningTargetRMS = False
                self.app.message.emit(f'Star [{wStar.number}] cannot be deleted', 2)
            else:
                text = f'Star [{wStar.number:02d}]: RMS of [{wStar.errorRMS:04.1f}] deleted'
                self.app.message.emit(text, 0)
            mount.getAlign()
        else:
            self.changeStyleDynamic(self.ui.runTargetRMS, 'running', 'false')
            self.ui.deleteWorstPoint.setEnabled(True)
            self.ui.clearModel.setEnabled(True)
            self.ui.refreshModel.setEnabled(True)
            mount.signals.alignDone.disconnect(self.clearRunTargetRMS)
            self.changeStyleDynamic(self.ui.cancelTargetRMS, 'cancel', 'false')
            self.app.message.emit('Optimizing done', 0)
        return True

    def runTargetRMS(self):
        """
        refreshModel disables interfering functions in gui and start reloading the
        alignment model from the mount computer. it connects a link to clearRefreshModel
        which enables the former disabled gui buttons and removes the link to the method.
        after it triggers the refresh of names, it finished, because behaviour is event
        driven

        :return: True for test purpose
        """

        self.app.message.emit('Start optimizing model', 0)
        self.runningTargetRMS = True
        self.app.mount.signals.alignDone.connect(self.clearRunTargetRMS)
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.ui.refreshModel.setEnabled(False)
        self.changeStyleDynamic(self.ui.runTargetRMS, 'running', 'true')
        self.clearRunTargetRMS()

        return True

    def cancelTargetRMS(self):
        """
        cancelTargetRMS just resets the running Flag for RMS target optimization -> enables
        the stop of optimization.

        :return:
        """

        self.runningTargetRMS = False
        self.changeStyleDynamic(self.ui.cancelTargetRMS, 'cancel', 'true')
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
