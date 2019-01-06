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
        ms = self.app.mount.signals
        ms.alignDone.connect(self.showModelPolar)
        ms.namesDone.connect(self.setNameList)

        self.ui.checkShowErrorValues.stateChanged.connect(self.showModelPolar)
        self.ui.refreshName.clicked.connect(self.refreshName)
        self.ui.loadName.clicked.connect(self.loadName)

    def initConfig(self):
        config = self.app.config['mainW']
        self.ui.checkShowErrorValues.setChecked(config.get('checkShowErrorValues', False))
        self.showModelPolar()
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['checkShowErrorValues'] = self.ui.checkShowErrorValues.isChecked()
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

    def clearMountGUI(self):
        """
        clearMountGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        self.setNameList()
        self.showModelPolar()
        return True

    def setNameList(self):
        """
        setNameList populates the list of model names in the main window. before adding the
        data, the existent list will be deleted.

        :return:    True if ok for testing
        """

        model = self.app.mount.model
        self.ui.nameList.clear()
        for name in model.nameList:
            self.ui.nameList.addItem(name)
        self.ui.nameList.sortItems()
        self.ui.nameList.update()
        return True

    def showModelPolar(self):
        """
        showModelPolar draws a polar plot of the align model stars and their errors in
        color. the basic setup of the plot is taking place in the central widget class.
        which is instantiated from there.

        :return:    True if ok for testing
        """

        # shortcuts
        model = self.app.mount.model
        location = self.app.mount.obsSite.location

        # check entry conditions for displaying a polar plot
        if model.starList is None:
            hasNoStars = True
        else:
            hasNoStars = len(model.starList) == 0
        hasNoLocation = location is None

        if hasNoStars or hasNoLocation:
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
        lat = location.latitude.degrees
        fig, axes = self.clearPolar(self.polarPlot)

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
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.runTargetRMS.setEnabled(True)
        self.ui.cancelTargetRMS.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.ui.refreshModel.setEnabled(True)
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
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.runTargetRMS.setEnabled(False)
        self.ui.cancelTargetRMS.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.ui.refreshModel.setEnabled(False)
        self.changeStyleDynamic(self.ui.refreshName, 'running', 'true')
        self.app.mount.getNames()
        return True

    def loadName(self):
        """

        :return:
        """

        if self.ui.nameList.currentItem() is None:
            self.app.message.emit('No model name selected', 2)
            return False
        modelName = self.ui.nameList.currentItem().text()
        suc = self.app.mount.model.loadName(modelName)
        if not suc:
            self.app.message.emit('Model [{0}] cannot be loaded'.format(modelName), 2)
            return False
        self.app.message.emit('Model [{0}] loaded'.format(modelName), 0)
        self.refreshModel()
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
        self.app.message.emit('Model names refreshed', 0)
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

        self.app.mount.signals.alignDone.connect(self.clearRefreshModel)
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.runTargetRMS.setEnabled(False)
        self.ui.cancelTargetRMS.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.changeStyleDynamic(self.ui.refreshModel, 'running', 'true')
        self.app.mount.getAlign()

