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
import os

# external packages
from PyQt5.QtCore import QPointF
import numpy as np
import cv2
import pyqtgraph as pg

# local import


class EditHorizon:
    """
    """

    def __init__(self):
        """
        """
        self.horizonPlot = None
        self.imageTerrain = None
        self.pointerHor = None
        self.ui.saveHorizonMask.clicked.connect(self.saveHorizonMask)
        self.ui.saveHorizonMaskAs.clicked.connect(self.saveHorizonMaskAs)
        self.ui.loadHorizonMask.clicked.connect(self.loadHorizonMask)
        self.ui.loadTerrainFile.clicked.connect(self.loadTerrainFile)
        self.ui.clearTerrainFile.clicked.connect(self.clearTerrainFile)
        self.ui.clearHorizonMask.clicked.connect(self.clearHorizonMask)
        self.ui.horizon.p[0].scene().sigMouseMoved.connect(self.mouseMovedHorizon)
        self.ui.addPositionToHorizon.clicked.connect(self.addActualPosition)
        self.app.mount.signals.pointDone.connect(self.drawPointerHor)
        self.ui.showTerrain.clicked.connect(self.drawHorizonTab)

        self.setIcons()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to
        the gui elements. if some initialisations have to be proceeded with the
        loaded persistent data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config.get('hemisphereW', {})
        fileName = config.get('horizonMaskFileName', '')
        self.ui.horizonMaskFileName.setText(fileName)
        self.app.data.loadHorizonP(fileName=fileName)

        fileName = config.get('terrainFileName', '')
        self.ui.terrainAlpha.setValue(config.get('terrainAlpha', 0.35))
        self.ui.azimuthShift.setValue(config.get('azimuthShift', 0))
        self.ui.altitudeShift.setValue(config.get('altitudeShift', 0))

        self.ui.azimuthShift.valueChanged.connect(self.drawHorizonTab)
        self.ui.altitudeShift.valueChanged.connect(self.drawHorizonTab)
        self.ui.terrainAlpha.valueChanged.connect(self.drawHorizonTab)

        self.ui.normalModeHor.clicked.connect(self.setOperationModeHor)
        self.ui.editModeHor.clicked.connect(self.setOperationModeHor)
        self.setTerrainFile(fileName)
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
        config['terrainFileName'] = self.ui.terrainFileName.text()
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
        self.wIcon(self.ui.loadTerrainFile, 'load')
        self.wIcon(self.ui.clearTerrainFile, 'trash')
        self.wIcon(self.ui.loadHorizonMask, 'load')
        self.wIcon(self.ui.saveHorizonMask, 'save')
        self.wIcon(self.ui.saveHorizonMaskAs, 'save')
        self.wIcon(self.ui.clearHorizonMask, 'trash')
        return True

    def colorChangeHorizon(self):
        """
        :return:
        """
        self.setIcons()
        return True

    def setTerrainFile(self, fileName):
        """
        :param fileName:
        :param ext:
        :return:
        """
        self.ui.terrainFileName.setText(fileName)
        terrainFile = self.app.mwGlob['configDir'] + '/' + fileName + '.jpg'
        if not os.path.isfile(terrainFile):
            self.imageTerrain = None
            return False

        img = cv2.imread(terrainFile, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        h2 = int(h / 2)
        img = img[0:h2, 0:w]
        img = cv2.resize(img, (1440, 360))
        img = cv2.flip(img, 0)
        self.imageTerrain = np.ones((480, 2880)) * 128
        self.imageTerrain[60:420, 0:1440] = img
        self.imageTerrain[60:420, 1440:2880] = img
        return True

    def loadTerrainFile(self):
        """
        :return:
        """
        folder = self.app.mwGlob['configDir']
        fileTypes = 'Terrain images (*.jpg)'
        loadFilePath, fileName, ext = self.openFile(
            self, 'Open terrain image', folder, fileTypes)
        if not loadFilePath:
            return False

        suc = self.setTerrainFile(fileName)
        if suc:
            self.ui.terrainFileName.setText(fileName)
            self.ui.showTerrain.setChecked(True)
            self.msg.emit(0, 'Hemisphere', 'Terrain',
                          f'Mask [{fileName}] loaded')
        else:
            self.msg.emit(2, 'Hemisphere', 'Terrain',
                          f'Image [{fileName}] cannot no be loaded')
        self.drawHorizonTab()
        return True

    def clearTerrainFile(self):
        """
        :return:
        """
        self.ui.terrainFileName.setText('')
        self.ui.showTerrain.setChecked(False)
        self.setTerrainFile('')
        self.drawHorizonTab()
        return True

    def loadHorizonMask(self):
        """
        :return: success
        """
        folder = self.app.mwGlob['configDir']
        fileTypes = 'Horizon mask files (*.hpts);; CSV Files (*.csv);; MW3 Files (*.txt)'
        loadFilePath, fileName, ext = self.openFile(self, 'Open horizon mask file',
                                                    folder, fileTypes)
        if not loadFilePath:
            return False

        suc = self.app.data.loadHorizonP(fileName=fileName, ext=ext)
        if suc:
            self.ui.horizonMaskFileName.setText(fileName)
            self.msg.emit(0, 'Hemisphere', 'Horizon',
                          f'Mask [{fileName}] loaded')
        else:
            self.msg.emit(2, 'Hemisphere', 'Horizon',
                          f'Mask [{fileName}] cannot no be loaded')

        self.app.redrawHemisphere.emit()
        self.app.redrawHorizon.emit()
        self.drawHorizonTab()
        return True

    def saveHorizonMask(self):
        """
        :return: success
        """
        fileName = self.ui.horizonMaskFileName.text()
        if not fileName:
            self.msg.emit(2, 'Hemisphere', 'Horizon',
                          'Mask file name not given')
            return False

        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.msg.emit(0, 'Hemisphere', 'Horizon',
                          f'Mask [{fileName}] saved')
        else:
            self.msg.emit(2, 'Hemisphere', 'Horizon',
                          f'Mask [{fileName}] cannot no be saved')
        return True

    def saveHorizonMaskAs(self):
        """
        :return: success
        """
        folder = self.app.mwGlob['configDir']
        saveFilePath, fileName, ext = self.saveFile(
            self, 'Save horizon mask file', folder, 'Horizon mask files (*.hpts)')
        if not saveFilePath:
            return False

        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.ui.horizonMaskFileName.setText(fileName)
            self.msg.emit(0, 'Hemisphere', 'Horizon',
                          f'Mask [{fileName}] saved')
        else:
            self.msg.emit(2, 'Hemisphere', 'Horizon',
                          f'Mask [{fileName}] cannot no be saved')
        return True

    def setOperationModeHor(self):
        """
        :return: success
        """
        if self.ui.editModeHor.isChecked():
            self.ui.addPositionToHorizon.setEnabled(True)
        else:
            self.ui.addPositionToHorizon.setEnabled(False)

        self.drawHorizonTab()
        return True

    def updateDataHorizon(self, x, y):
        """
        :return:
        """
        self.horizonPlot.setData(x=x, y=y)
        hp = [(y, x) for x, y in zip(x, y)]
        self.app.data.horizonP = hp
        self.app.redrawHorizon.emit()
        return True

    def clearHorizonMask(self):
        """
        :return:
        """
        self.app.data.horizonP = []
        self.ui.horizonMaskFileName.setText('')
        self.app.redrawHorizon.emit()
        self.drawHorizonTab()
        return True

    def addActualPosition(self):
        """
        :return:
        """
        vb = self.ui.horizon.p[0].getViewBox()
        az = self.app.mount.obsSite.Az
        alt = self.app.mount.obsSite.Alt
        if alt is None and az is None:
            return False
        az = az.degrees
        alt = alt.degrees
        index = vb.getNearestPointIndex(QPointF(az, alt))
        if index is not None:
            vb.addUpdate(index, QPointF(az, alt))
        return True

    def prepareHorizonView(self):
        """
        :return:
        """
        plotItem = self.ui.horizon.p[0]
        self.preparePlotItem(plotItem)
        self.pointerHor = None
        return True

    def drawHorizonView(self):
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

    def setupPointerHor(self):
        """
        :return:
        """
        plotItem = self.ui.horizon.p[0]
        symbol = self.makePointer()
        self.pointerHor = pg.ScatterPlotItem(symbol=symbol, size=40)
        self.pointerHor.setData(x=[0], y=[45])
        self.pointerHor.setPen(pg.mkPen(color=self.M_PINK))
        self.pointerHor.setBrush(pg.mkBrush(color=self.M_PINK + '20'))
        self.pointerHor.setZValue(10)
        plotItem.addItem(self.pointerHor)
        return True

    def drawPointerHor(self):
        """
        :return:
        """
        if self.pointerHor is None:
            return False

        obsSite = self.app.mount.obsSite
        if obsSite.Alt is None or obsSite.Az is None:
            self.pointerHor.setVisible(False)
            return False

        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerHor.setData(x=[az], y=[alt])
        self.pointerHor.setVisible(True)
        return True

    def setupHorizonView(self):
        """
        :return:
        """
        plotItem = self.ui.horizon.p[0]
        if self.ui.editModeHor.isChecked():
            self.horizonPlot = pg.PlotDataItem(
                symbolBrush=pg.mkBrush(color=self.M_PINK + '40'),
                symbolPen=pg.mkPen(color=self.M_PINK1, width=2),
                brush=pg.mkBrush(color=self.M_PINK + '40'),
                pen=pg.mkPen(color=self.M_PINK1, width=2),
                symbolSize=10, symbol='o', connect='all')
            plotItem.addItem(self.horizonPlot)
            vb = plotItem.getViewBox()
            vb.setPlotDataItem(self.horizonPlot)
            vb.updateData = self.updateDataHorizon
            vb.setOpts(enableLimitX=True)
        else:
            self.horizonPlot = pg.PlotDataItem(
                symbolBrush=pg.mkBrush(color=self.M_BLUE + '40'),
                symbolPen=pg.mkPen(color=self.M_BLUE1, width=2),
                brush=pg.mkBrush(color=self.M_BLUE + '40'),
                pen=pg.mkPen(color=self.M_BLUE1, width=2),
                symbolSize=5, symbol='o', connect='all')
            plotItem.addItem(self.horizonPlot)
        return True

    def drawHorizonTab(self):
        """
        :return:
        """
        self.prepareHorizonView()
        if self.ui.showTerrain.isChecked():
            self.drawTerrainMask(self.ui.horizon.p[0])
        self.setupHorizonView()
        self.drawHorizonView()
        if self.ui.editModeHor.isChecked():
            self.setupPointerHor()
            self.drawPointerHor()
        return True
