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
import numpy as np
import pyqtgraph as pg

# local import


class EditHorizon:
    """
    """

    def __init__(self):
        """
        """
        self.horizonPlot = None
        self.ui.saveHorizonMask.clicked.connect(self.saveHorizonMask)
        self.ui.saveHorizonMaskAs.clicked.connect(self.saveHorizonMaskAs)
        self.ui.loadHorizonMask.clicked.connect(self.loadHorizonMask)
        self.ui.clearHorizonMask.clicked.connect(self.clearHorizonMask)
        self.ui.horizon.p[0].scene().sigMouseMoved.connect(self.mouseMovedHorizon)
        # self.ui.addPositionToHorizon.clicked.connect()
        self.ui.showTerrain.clicked.connect(self.drawEditHorizon)

        self.setIcons()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['hemisphereW']
        fileName = config.get('horizonMaskFileName', '')
        self.ui.horizonMaskFileName.setText(fileName)
        self.app.data.loadHorizonP(fileName=fileName)

        self.ui.terrainAlpha.setValue(config.get('terrainAlpha', 0.35))
        self.ui.azimuthShift.setValue(config.get('azimuthShift', 0))
        self.ui.altitudeShift.setValue(config.get('altitudeShift', 0))

        self.ui.azimuthShift.valueChanged.connect(self.drawEditHorizon)
        self.ui.altitudeShift.valueChanged.connect(self.drawEditHorizon)
        self.ui.terrainAlpha.valueChanged.connect(self.drawEditHorizon)
        self.drawEditHorizon()
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['hemisphereW']
        config['horizonMaskFileName'] = self.ui.horizonMaskFileName.text()
        config['terrainAlpha'] = self.ui.terrainAlpha.value()
        config['azimuthShift'] = self.ui.azimuthShift.value()
        config['altitudeShift'] = self.ui.altitudeShift.value()
        return True

    def mouseMovedHorizon(self, pos):
        """
        :param pos:
        :return:
        """
        plotItem = self.ui.horizon.p[0]
        self.mouseMoved(plotItem, pos)
        return True

    def setIcons(self):
        """
        :return:
        """
        self.wIcon(self.ui.loadHorizonMask, 'load')
        self.wIcon(self.ui.saveHorizonMask, 'save')
        self.wIcon(self.ui.saveHorizonMaskAs, 'save')
        self.wIcon(self.ui.clearHorizonMask, 'trash')
        return True

    def colorChange(self):
        """
        :return:
        """
        self.setIcons()
        return True

    def loadHorizonMask(self):
        """
        :return: success
        """
        folder = self.app.mwGlob['configDir']
        fileTypes = 'Horizon mask files (*.hpts);; CSV Files (*.csv);; MW3 Files (*.txt)'
        loadFilePath, fileName, ext = self.openFile(self,
                                                    'Open horizon mask file',
                                                    folder,
                                                    fileTypes)
        if not loadFilePath:
            return False

        suc = self.app.data.loadHorizonP(fileName=fileName, ext=ext)
        if suc:
            self.ui.horizonMaskFileName.setText(fileName)
            self.app.message.emit(f'Horizon mask [{fileName}] loaded', 0)
        else:
            self.app.message.emit(f'Horizon mask [{fileName}] cannot no be loaded', 2)

        self.app.redrawHemisphere.emit()
        self.horizonPlot = None
        self.drawEditHorizon()
        return True

    def saveHorizonMask(self):
        """
        :return: success
        """
        fileName = self.ui.horizonMaskFileName.text()
        if not fileName:
            self.app.message.emit('Horizon mask file name not given', 2)
            return False

        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.app.message.emit(f'Horizon mask [{fileName}] saved', 0)
        else:
            self.app.message.emit(f'Horizon mask [{fileName}] cannot no be saved', 2)
        return True

    def saveHorizonMaskAs(self):
        """
        :return: success
        """
        folder = self.app.mwGlob['configDir']
        saveFilePath, fileName, ext = self.saveFile(self,
                                                    'Save horizon mask file',
                                                    folder,
                                                    'Horizon mask files (*.hpts)',
                                                    )
        if not saveFilePath:
            return False

        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.ui.horizonMaskFileName.setText(fileName)
            self.app.message.emit(f'Horizon mask [{fileName}] saved', 0)
        else:
            self.app.message.emit(f'Horizon mask [{fileName}] cannot no be saved', 2)
        return True

    def storeHorizonData(self):
        """
        :return:
        """
        data = self.horizonPlot.curve.getData()
        hp = [(y, x) for x, y in zip(data[0], data[1])]
        self.app.data.horizonP = hp
        self.app.redrawHorizon.emit()
        return True

    def clearHorizonMask(self):
        """
        :return:
        """
        self.app.data.horizonP = []
        self.ui.horizonMaskFileName.setText('')
        self.app.redrawHemisphere.emit()
        self.drawEditHorizon()
        return True

    def drawHorizonData(self):
        """
        :return:
        """
        hp = self.app.data.horizonP
        if len(hp) == 0:
            return False
        alt, az = zip(*hp)
        alt = np.array(alt)
        az = np.array(az)
        self.horizonPlot.setData(x=az, y=alt)
        return True

    def drawEditHorizon(self):
        """
        :return:
        """
        plotItem = self.ui.horizon.p[0]
        self.preparePlotItem(plotItem)
        self.horizonPlot = pg.PlotDataItem(
            symbolBrush=pg.mkBrush(color=self.M_PINK + '40'),
            symbolPen=pg.mkPen(color=self.M_PINK1, width=2),
            brush=pg.mkBrush(color=self.M_PINK + '40'),
            pen=pg.mkPen(color=self.M_PINK1, width=2),
            symbolSize=4, symbol='o', connect='all')
        plotItem.addItem(self.horizonPlot)
        vb = plotItem.getViewBox()
        vb.setPlotDataItem(self.horizonPlot)
        vb.setOpts(enableLimitX=True)
        self.horizonPlot.sigPlotChanged.connect(self.storeHorizonData)

        if self.ui.showTerrain.isChecked():
            self.drawTerrainMask(plotItem)
        self.drawHorizonData()
        return True
