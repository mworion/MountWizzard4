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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages
import numpy as np
import sep
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from astropy.io import fits
from PIL import Image
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter

# local import
from mountcontrol.convert import convertToDMS, convertToHMS
from base.fitsHeader import getCoordinates, getSQM, getExposure, getScale
from gui.utilities import toolsQtWidget
from gui.widgets import image_ui
from base.tpool import Worker


class ImageWindowSignals(QObject):
    """
    """
    __all__ = ['ImageWindowSignals']
    solveImage = pyqtSignal(object)
    showTitle = pyqtSignal(object)


class ImageWindow(toolsQtWidget.MWidget):
    """
    """
    __all__ = ['ImageWindow']

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool
        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.signals = ImageWindowSignals()

        self.barItem = None
        self.imageItem = None

        self.imageFileName = ''
        self.imageFileNameOld = ''
        self.expTime = 1
        self.binning = 1
        self.image = None
        self.folder = ''
        self.header = None
        self.imageStack = None
        self.numberStack = 0
        self.objs = None
        self.bkg = None
        self.HFD = None
        self.filterConst = None
        self.xm = None
        self.ym = None
        self.scale = 5
        self.aberrationSize = 250
        self.result = None
        self.medianHFD = None
        self.innerHFD = None
        self.outerHFD = None
        self.pen = pg.mkPen(color=self.M_BLUE, width=3)
        self.font = QFont(self.window().font().family(), 16)
        self.font.setBold(True)

        self.deviceStat = {
            'expose': False,
            'exposeN': False,
            'solve': False,
        }

        self.app.update1s.connect(self.updateWindowsStats)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
        config = self.app.config['imageW']
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)

        self.ui.color.setCurrentIndex(config.get('color', 0))
        self.ui.tabImage.setCurrentIndex(config.get('tabImage', 0))
        self.imageFileName = config.get('imageFileName', '')
        self.folder = self.app.mwGlob.get('imageDir', '')
        self.ui.stackImages.setChecked(config.get('stackImages', False))
        self.ui.showCrosshair.setChecked(config.get('showCrosshair', False))
        self.ui.aspectLocked.setChecked(config.get('aspectLocked', False))
        self.ui.autoSolve.setChecked(config.get('autoSolve', False))
        self.ui.embedData.setChecked(config.get('embedData', False))
        self.ui.enablePhotometry.setChecked(config.get('enablePhotometry', False))
        self.ui.offsetTiltAngle.setValue(config.get('offsetTiltAngle', 0))
        self.setCrosshair()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
        config = self.app.config['imageW']
        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        config['color'] = self.ui.color.currentIndex()
        config['tabImage'] = self.ui.tabImage.currentIndex()
        config['imageFileName'] = self.imageFileName
        config['stackImages'] = self.ui.stackImages.isChecked()
        config['showCrosshair'] = self.ui.showCrosshair.isChecked()
        config['aspectLocked'] = self.ui.aspectLocked.isChecked()
        config['autoSolve'] = self.ui.autoSolve.isChecked()
        config['embedData'] = self.ui.embedData.isChecked()
        config['enablePhotometry'] = self.ui.enablePhotometry.isChecked()
        config['offsetTiltAngle'] = self.ui.offsetTiltAngle.value()
        return True

    def showWindow(self):
        """
        showWindow prepares all data for showing the window, plots the image and
        show it. afterwards all necessary signal / slot connections will be
        established.

        :return: true for test purpose
        """
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.setBarColor)
        self.ui.showCrosshair.clicked.connect(self.setCrosshair)
        self.ui.enablePhotometry.clicked.connect(self.preparePhotometry)
        self.ui.aspectLocked.clicked.connect(self.setAspectLocked)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.stackImages.clicked.connect(self.clearStack)
        self.ui.abortImage.clicked.connect(self.abortImage)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.ui.image.barItem.sigLevelsChangeFinished.connect(self.copyLevels)
        self.ui.offsetTiltAngle.valueChanged.connect(self.showTabTiltTriangle)
        self.signals.solveImage.connect(self.solveImage)
        self.signals.showTitle.connect(self.showTitle)
        self.app.showImage.connect(self.showImage)
        self.app.colorChange.connect(self.colorChange)
        self.show()
        self.showCurrent()
        self.setAspectLocked()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return: True for test purpose
        """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.ui.image.colorChange()
        self.pen = pg.mkPen(color=self.M_BLUE)
        self.showCurrent()
        return True

    def updateWindowsStats(self):
        """
        :return: true for test purpose
        """
        if self.deviceStat.get('expose', False):
            self.ui.exposeN.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortImage.setEnabled(True)
        elif self.deviceStat.get('exposeN', False):
            self.ui.expose.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortImage.setEnabled(True)
        else:
            self.ui.solve.setEnabled(True)
            self.ui.expose.setEnabled(True)
            self.ui.exposeN.setEnabled(True)
            self.ui.load.setEnabled(True)
            self.ui.abortImage.setEnabled(False)

        if self.deviceStat.get('solve', False):
            self.ui.abortSolve.setEnabled(True)
        else:
            self.ui.abortSolve.setEnabled(False)

        if not self.app.deviceStat.get('camera', False):
            self.ui.expose.setEnabled(False)
            self.ui.exposeN.setEnabled(False)

        if not self.app.deviceStat.get('astrometry', False):
            self.ui.solve.setEnabled(False)

        if self.deviceStat.get('expose', False):
            self.changeStyleDynamic(self.ui.expose, 'running', True)
        elif self.deviceStat.get('exposeN', False):
            self.changeStyleDynamic(self.ui.exposeN, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.expose, 'running', False)
            self.changeStyleDynamic(self.ui.exposeN, 'running', False)

        if self.deviceStat.get('solve', False):
            self.changeStyleDynamic(self.ui.solve, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.solve, 'running', False)

        return True

    def showTitle(self, text):
        """
        :param text:
        :return:
        """
        fileName = os.path.basename(self.imageFileName)
        self.setWindowTitle(f'Imaging:   {fileName}   {text}')
        return True

    def selectImage(self):
        """
        :return: success
        """
        val = self.openFile(self, 'Select image file', self.folder,
                            'FITS files (*.fit*)', enableDir=True)
        loadFilePath, name, ext = val
        if not name:
            self.app.message.emit('No image selected', 0)
            return False

        self.signals.showTitle.emit('')
        self.imageFileName = loadFilePath
        self.app.message.emit(f'Image selected:      [{name}]', 0)
        self.folder = os.path.dirname(loadFilePath)
        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(self.imageFileName)
        self.app.showImage.emit(self.imageFileName)
        return True

    def setBarColor(self):
        """
        :return:
        """
        cMap = ['CET-L2', 'plasma', 'cividis', 'magma', 'CET-D1A']
        colorMap = cMap[self.ui.color.currentIndex()]
        self.ui.image.setColorMap(colorMap)
        self.ui.imageSource.setColorMap(colorMap)
        self.ui.background.setColorMap(colorMap)
        self.ui.backgroundRMS.setColorMap(colorMap)
        self.ui.hfd.setColorMap(colorMap)
        self.ui.tiltSquare.setColorMap(colorMap)
        self.ui.tiltTriangle.setColorMap(colorMap)
        self.ui.roundness.setColorMap(colorMap)
        self.ui.aberration.setColorMap(colorMap)
        return True

    def copyLevels(self):
        """
        :return:
        """
        level = self.ui.image.barItem.levels()
        self.ui.tiltSquare.barItem.setLevels(level)
        self.ui.tiltTriangle.barItem.setLevels(level)
        self.ui.aberration.barItem.setLevels(level)
        self.ui.imageSource.barItem.setLevels(level)
        return True

    def setCrosshair(self):
        """
        :return:
        """
        self.ui.image.showCrosshair(self.ui.showCrosshair.isChecked())
        return True

    def setAspectLocked(self):
        """
        :return:
        """
        isLocked = self.ui.aspectLocked.isChecked()
        self.ui.image.p[0].setAspectLocked(isLocked)
        self.ui.imageSource.p[0].setAspectLocked(isLocked)
        self.ui.tiltSquare.p[0].setAspectLocked(isLocked)
        self.ui.tiltTriangle.p[0].setAspectLocked(isLocked)
        self.ui.background.p[0].setAspectLocked(isLocked)
        self.ui.backgroundRMS.p[0].setAspectLocked(isLocked)
        self.ui.hfd.p[0].setAspectLocked(isLocked)
        self.ui.roundness.p[0].setAspectLocked(isLocked)
        return True

    def calcAberrationInspectView(self, img):
        """
        :param img:
        :return:
        """
        size = self.aberrationSize
        h, w = img.shape
        if w < 3 * size or h < 3 * size:
            return img

        dw = int((w - 3 * size) / 2)
        dh = int((h - 3 * size) / 2)

        img = np.delete(img, np.s_[size:size + dh], axis=0)
        img = np.delete(img, np.s_[size * 2:size * 2 + dh], axis=0)
        img = np.delete(img, np.s_[size:size + dw], axis=1)
        img = np.delete(img, np.s_[size * 2:size * 2 + dw], axis=1)
        return img

    def workerCalcTiltValuesSquare(self):
        """
        :return:
        """
        h, w = self.image.shape
        stepY = int(h / 3)
        stepX = int(w / 3)

        xRange = [0, stepX, 2 * stepX, 3 * stepX]
        yRange = [0, stepY, 2 * stepY, 3 * stepY]
        x = self.objs['x']
        y = self.objs['y']
        segHFD = np.zeros((3, 3))
        for ix in range(3):
            for iy in range(3):
                xMin = xRange[ix]
                xMax = xRange[ix + 1]
                yMin = yRange[iy]
                yMax = yRange[iy + 1]
                hfd = self.HFD[(x > xMin) & (x < xMax) & (y > yMin) & (y < yMax)]
                med_hfd = np.median(hfd)
                segHFD[ix][iy] = med_hfd
        return segHFD

    def workerCalcTiltValuesTriangle(self):
        """
        :return:
        """
        h, w = self.image.shape
        x = self.objs['x'] - w / 2
        y = self.objs['y'] - h / 2
        r = min(h / 2, w / 2)
        mask1 = np.sqrt(h * h + w * w) * 0.25 < r
        mask2 = np.sqrt(h * h + w * w) > r
        segHFD = np.zeros(36)
        angles = np.mod(np.arctan2(y, x), 2*np.pi)
        rangeA = np.radians(range(0, 361, 10))
        for i in range(36):
            mask3 = rangeA[i] < angles
            mask4 = rangeA[i + 1] > angles
            segHFD[i] = np.median(self.HFD[mask1 & mask2 & mask3 & mask4])
        return np.concatenate([segHFD, segHFD])

    def baseCalcTabInfo(self):
        """
        :return:
        """
        h, w = self.image.shape

        rangeX = np.linspace(0, w, int(w / self.scale))
        rangeY = np.linspace(0, h, int(h / self.scale))
        self.xm, self.ym = np.meshgrid(rangeX, rangeY)
        self.filterConst = int(w / self.scale / 2)

        x = self.objs['x'] - w / 2
        y = self.objs['y'] - h / 2
        self.medianHFD = np.median(self.HFD)
        r = np.sqrt(x * x + y * y)
        maskOuter = np.sqrt(h * h / 4 + w * w / 4) * 0.75 < r
        maskInner = np.sqrt(h * h / 4 + w * w / 4) * 0.25 > r
        self.outerHFD = np.median(self.HFD[maskOuter])
        self.innerHFD = np.median(self.HFD[maskInner])
        return True

    def showTabRaw(self):
        """
        :return:
        """
        self.ui.image.setImage(imageDisp=self.image)
        self.setCrosshair()
        QApplication.processEvents()
        return True

    def workerShowTabHFD(self):
        """
        :return:
        """
        img = griddata((self.objs['x'], self.objs['y']), self.HFD, (self.xm,
                                                                    self.ym),
                       method='nearest', fill_value=np.min(self.HFD))
        img = uniform_filter(img, size=self.filterConst)
        return img

    def showTabHFD(self, img):
        """
        :param img:
        :return:
        """
        self.ui.tabImage.setTabEnabled(1, True)
        self.ui.hfd.setImage(imageDisp=img)
        self.ui.hfd.p[0].showAxes(False, showValues=False)
        self.ui.hfd.p[0].setMouseEnabled(x=False, y=False)
        hfdPercentile10 = np.percentile(self.HFD, 90)
        self.ui.hfdPercentile.setText(f'{hfdPercentile10:1.1f}')
        medianHFD = np.median(self.HFD)
        self.ui.medianHFD.setText(f'{medianHFD:1.2f}')
        self.ui.numberStars.setText(f'{len(self.HFD):1.0f}')
        QApplication.processEvents()
        return True

    def showTabTiltSquare(self, segHFD):
        """
        :param segHFD:
        :return:
        """
        h, w = self.image.shape
        self.ui.tiltSquare.p[0].clear()
        self.ui.tiltSquare.setImage(self.image)
        self.ui.tiltSquare.p[0].showAxes(False, showValues=False)
        self.ui.tiltSquare.p[0].setMouseEnabled(x=False, y=False)
        self.ui.tiltSquare.barItem.setVisible(False)
        for ix in range(3):
            for iy in range(3):
                text = f'{segHFD[ix][iy]:1.2f}'
                textItem = pg.TextItem(anchor=(0.5, 0.5), color=self.M_BLUE)
                textItem.setText(text)
                textItem.setFont(self.font)
                posX = ix * w / 3 + w / 6
                posY = iy * h / 3 + h / 6
                textItem.setPos(posX, posY)
                self.ui.tiltSquare.p[0].addItem(textItem)
        for ix in range(1, 3):
            posX = ix * w / 3
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(posX, 0, posX, h)
            self.ui.tiltSquare.p[0].addItem(lineItem)
        for iy in range(1, 3):
            posY = iy * h / 3
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(0, posY, w, posY)
            self.ui.tiltSquare.p[0].addItem(lineItem)

        best = np.min([segHFD[0][0], segHFD[0][2], segHFD[2][0], segHFD[2][2]])
        worst = np.max([segHFD[0][0], segHFD[0][2], segHFD[2][0], segHFD[2][2]])
        tiltDiff = worst - best
        tiltPercent = 100 * tiltDiff / self.medianHFD

        t = f'{tiltDiff:1.2f} ({tiltPercent:1.0f}%)'
        self.ui.textSquareTiltHFD.setText(t)

        offAxisDiff = self.outerHFD - segHFD[1][1]
        offAxisPercent = 100 * offAxisDiff / self.medianHFD
        t = f'{offAxisDiff:1.2f} ({offAxisPercent:1.0f}%)'
        self.ui.textSquareTiltOffAxis.setText(t)
        self.ui.squareMedianHDF.setText(f'{self.medianHFD:1.2f}')
        self.ui.squareNumberStars.setText(f'{len(self.HFD):1.0f}')

        self.ui.tabImage.setTabEnabled(2, True)
        QApplication.processEvents()
        return True

    def showTabTiltTriangle(self, segHFD):
        """
        :param segHFD:
        :return:
        """
        h, w = self.image.shape
        r = min(h, w) / 2
        cx = w / 2
        cy = h / 2

        self.ui.tiltTriangle.p[0].clear()
        self.ui.tiltTriangle.setImage(self.image)
        self.ui.tiltTriangle.p[0].showAxes(False, showValues=False)
        self.ui.tiltTriangle.p[0].setMouseEnabled(x=False, y=False)
        self.ui.tiltTriangle.barItem.setVisible(False)
        ellipseItem = pg.QtWidgets.QGraphicsEllipseItem()
        ellipseItem.setRect(cx - r, cy - r, 2 * r, 2 * r)
        ellipseItem.setPen(self.pen)
        self.ui.tiltTriangle.p[0].addItem(ellipseItem)
        r25 = 0.25 * r
        ellipseItem = pg.QtWidgets.QGraphicsEllipseItem()
        ellipseItem.setRect(cx - r25, cy - r25, 2 * r25, 2 * r25)
        ellipseItem.setPen(self.pen)
        self.ui.tiltTriangle.p[0].addItem(ellipseItem)

        offsetTiltAngle = self.ui.offsetTiltAngle.value()

        text = f'{self.innerHFD:1.2f}'
        textItem = pg.TextItem(anchor=(0.5, 0.5), color=self.M_BLUE)
        textItem.setText(text)
        textItem.setFont(self.font)
        textItem.setPos(cx, cy)
        self.ui.tiltTriangle.p[0].addItem(textItem)
        segData = [0, 0, 0]

        for i, angle in enumerate(range(0, 360, 120)):
            angleSep = np.radians(angle + offsetTiltAngle + 210)
            angleText = np.radians(angle + offsetTiltAngle + 270)
            posX1 = cx + r25 * np.cos(angleSep)
            posX2 = cx + r * np.cos(angleSep)
            posY1 = cy + r25 * np.sin(angleSep)
            posY2 = cy + r * np.sin(angleSep)
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setLine(posX1, posY1, posX2, posY2)
            lineItem.setPen(self.pen)
            self.ui.tiltTriangle.p[0].addItem(lineItem)
            startIndexSeg = int((angle + offsetTiltAngle + 210) / 10)
            endIndexSeg = int((angle + offsetTiltAngle + 330) / 10)
            segData[i] = np.mean(segHFD[startIndexSeg:endIndexSeg])
            text = f'{segData[i]:1.2f}'
            textItem = pg.TextItem(anchor=(0.5, 0.5), color=self.M_BLUE)
            textItem.setFont(self.font)
            textItem.setText(text)
            posX = cx + r * 0.625 * np.cos(angleText)
            posY = cy + r * 0.625 * np.sin(angleText)
            textItem.setPos(posX, posY)
            self.ui.tiltTriangle.p[0].addItem(textItem)

        best = np.min(segData)
        worst = np.max(segData)
        tiltDiff = worst - best
        tiltPercent = 100 * tiltDiff / self.medianHFD

        t = f'{tiltDiff:1.2f} ({tiltPercent:1.0f}%)'
        self.ui.textTriangleTiltHFD.setText(t)

        offAxisDiff = self.outerHFD - self.innerHFD
        offAxisPercent = 100 * offAxisDiff / self.medianHFD
        t = f'{offAxisDiff:1.2f} ({offAxisPercent:1.0f}%)'
        self.ui.textTriangleTiltOffAxis.setText(t)
        self.ui.triangleMedianHDF.setText(f'{self.medianHFD:1.2f}')
        self.ui.triangleNumberStars.setText(f'{len(self.HFD):1.0f}')

        self.ui.tabImage.setTabEnabled(3, True)
        QApplication.processEvents()
        return True

    def workerShowTabRoundness(self):
        """
        :return:
        """
        a = self.objs['a']
        b = self.objs['b']
        aspectRatio = np.maximum(a/b, b/a)
        minB, maxB = np.percentile(aspectRatio, (50, 95))
        img = griddata((self.objs['x'], self.objs['y']), aspectRatio, (self.xm,
                                                                       self.ym),
                       method='linear', fill_value=np.min(aspectRatio))
        img = uniform_filter(img, size=self.filterConst)
        return aspectRatio, img, minB, maxB

    def showTabRoundness(self, result):
        """
        :param result:
        :return:
        """
        self.ui.tabImage.setTabEnabled(4, True)
        aspectRatio, img, minB, maxB = result
        self.ui.roundness.setImage(imageDisp=img)
        self.ui.roundness.p[0].showAxes(False, showValues=False)
        self.ui.roundness.p[0].setMouseEnabled(x=False, y=False)
        self.ui.roundness.barItem.setLevels((minB, maxB))
        aspectRatioPercentile10 = np.percentile(aspectRatio, 90)
        self.ui.aspectRatioPercentile.setText(f'{aspectRatioPercentile10:1.1f}')
        QApplication.processEvents()
        return True

    def showTabAberrationInspect(self):
        """
        :return:
        """
        self.ui.tabImage.setTabEnabled(5, True)
        self.ui.aberration.barItem.setVisible(False)
        abb = self.calcAberrationInspectView(self.image)
        h, w = abb.shape
        self.ui.aberration.p[0].clear()
        self.ui.aberration.setImage(abb)
        self.ui.aberration.p[0].setAspectLocked(True)
        self.ui.aberration.p[0].showAxes(False, showValues=False)
        self.ui.aberration.p[0].setMouseEnabled(x=False, y=False)
        for ix in range(1, 3):
            posX = ix * w / 3
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(posX, 0, posX, h)
            self.ui.aberration.p[0].addItem(lineItem)
        for iy in range(1, 3):
            posY = iy * h / 3
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(0, posY, w, posY)
            self.ui.aberration.p[0].addItem(lineItem)
        QApplication.processEvents()
        self.ui.aberration.p[0].getViewBox().rightMouseRange()
        return True

    def showTabImageSources(self):
        """
        :return:
        """
        self.ui.tabImage.setTabEnabled(6, True)
        self.ui.imageSource.setImage(imageDisp=self.image)
        for i in range(len(self.objs)):
            self.ui.imageSource.addEllipse(self.objs['x'][i], self.objs['y'][i],
                                           self.objs['a'][i], self.objs['b'][i],
                                           self.objs['theta'][i])
        QApplication.processEvents()
        return True

    def showTabBackground(self):
        """
        :return:
        """
        self.ui.tabImage.setTabEnabled(7, True)
        back = self.bkg.back()
        maxB = np.max(back) / self.bkg.globalback
        minB = np.min(back) / self.bkg.globalback
        img = self.bkg.back() / self.bkg.globalback
        img = uniform_filter(img, size=self.filterConst)
        self.ui.background.setImage(imageDisp=img)
        self.ui.background.barItem.setLevels((minB, maxB))
        QApplication.processEvents()
        return True

    def showTabBackgroundRMS(self):
        """
        :return:
        """
        self.ui.tabImage.setTabEnabled(8, True)
        img = self.bkg.rms()
        img = uniform_filter(img, size=self.filterConst)
        self.ui.backgroundRMS.setImage(imageDisp=img)
        QApplication.processEvents()
        return True

    def showTabImages(self):
        """
        :return:
        """
        self.setBarColor()
        self.showTabRaw()
        self.changeStyleDynamic(self.ui.headerGroup, 'running', False)
        if self.HFD is None:
            return False

        self.baseCalcTabInfo()

        worker = Worker(self.workerShowTabHFD)
        worker.signals.result.connect(self.showTabHFD)
        self.threadPool.start(worker)

        worker = Worker(self.workerShowTabRoundness)
        worker.signals.result.connect(self.showTabRoundness)
        self.threadPool.start(worker)

        worker = Worker(self.workerCalcTiltValuesSquare)
        worker.signals.result.connect(self.showTabTiltSquare)
        self.threadPool.start(worker)

        worker = Worker(self.workerCalcTiltValuesTriangle)
        worker.signals.result.connect(self.showTabTiltTriangle)
        self.threadPool.start(worker)

        self.showTabBackground()
        self.showTabAberrationInspect()
        self.showTabImageSources()
        self.showTabBackgroundRMS()

        self.changeStyleDynamic(self.ui.tabImage, 'running', False)
        return True

    def workerPreparePhotometry(self):
        """
        :return:
        """
        self.bkg = sep.Background(self.image, fthresh=np.median(self.image))
        image_sub = self.image - self.bkg

        objs = sep.extract(image_sub, 3.0, err=self.bkg.globalrms,
                           filter_type='matched', minarea=11)

        # remove objects without need
        r = np.sqrt(objs['a'] * objs['a'] + objs['b'] * objs['b'])
        mask = (r < 10) & (r > 0.8)
        objs = objs[mask]

        kronRad, krFlag = sep.kron_radius(
            image_sub, objs['x'], objs['y'], objs['a'], objs['b'], objs['theta'], 6.0)

        flux, fluxErr, flag = sep.sum_ellipse(
            image_sub, objs['x'], objs['y'], objs['a'], objs['b'], objs['theta'],
            2.5 * kronRad, subpix=1)

        flag |= krFlag
        r_min = 1.75

        useCircle = kronRad * np.sqrt(objs['a'] * objs['b']) < r_min
        cFlux, cFluxErr, cFlag = sep.sum_circle(
            image_sub, objs['x'][useCircle], objs['y'][useCircle], r_min, subpix=1)

        flux[useCircle] = cFlux
        fluxErr[useCircle] = cFluxErr
        flag[useCircle] = cFlag

        radius, _ = sep.flux_radius(
            image_sub, objs['x'], objs['y'], 6.0 * objs['a'], 0.5,
            normflux=flux, subpix=5)

        sn = flux / np.sqrt(flux + 99 * 99 * 3.1415926 * self.bkg.globalrms / 1.46)
        mask = (sn > 10) & (2 * radius < 20)

        # to get HFD
        self.objs = objs[mask]
        self.HFD = 2 * radius[mask]
        return True

    def clearGui(self):
        """
        :return:
        """
        self.signals.showTitle.emit('')
        self.ui.medianHFD.setText('')
        self.ui.hfdPercentile.setText('')
        self.ui.numberStars.setText('')
        self.ui.aspectRatioPercentile.setText('')
        self.ui.image.setImage(None)
        for i in range(1, self.ui.tabImage.count()):
            self.ui.tabImage.setTabEnabled(i, False)
        self.changeStyleDynamic(self.ui.tabImage, 'running', False)
        return True

    def preparePhotometry(self):
        """
        :return:
        """
        doPhotometry = self.ui.enablePhotometry.isChecked()
        if doPhotometry:
            self.ui.stackImages.setChecked(False)
            self.changeStyleDynamic(self.ui.tabImage, 'running', True)
            worker = Worker(self.workerPreparePhotometry)
            worker.signals.finished.connect(self.showTabImages)
            self.threadPool.start(worker)
        else:
            self.clearGui()
            self.objs = None
            self.bkg = None
            self.HFD = None
            self.showTabImages()
        return True

    def stackImages(self):
        """
        :return:
        """
        if not self.ui.stackImages.isChecked():
            self.imageStack = None
            return False

        if np.shape(self.image) != np.shape(self.imageStack):
            self.imageStack = None

        if self.imageStack is None:
            self.imageStack = self.image
            self.numberStack = 1
        else:
            self.imageStack = np.add(self.imageStack, self.image)
            self.numberStack += 1

        self.image = self.imageStack / self.numberStack
        self.signals.showTitle.emit(f'stacked: {self.numberStack:3.0f}')
        return True

    def clearStack(self):
        """
        :return:
        """
        if not self.ui.stackImages.isChecked():
            self.imageStack = None
            self.numberStack = 0
            self.signals.showTitle.emit('')
            return False
        else:
            self.ui.enablePhotometry.setChecked(False)
        return True

    def debayerImage(self, image, pattern):
        """
        :param: image:
        :param: pattern:
        :return:
        """
        w = image.shape[0]
        h = image.shape[1]
        if pattern == 'GBRG':
            R = image[1::2, 0::2]
            B = image[0::2, 1::2]
            G0 = image[0::2, 0::2]
            G1 = image[1::2, 1::2]

        elif pattern == 'RGGB':
            R = image[0::2, 0::2]
            B = image[1::2, 1::2]
            G0 = image[0::2, 1::2]
            G1 = image[1::2, 0::2]

        elif pattern == 'GRBG':
            R = image[0::2, 1::2]
            B = image[1::2, 0::2]
            G0 = image[0::2, 0::2]
            G1 = image[1::2, 1::2]

        elif pattern == 'BGGR':
            R = image[1::2, 1::2]
            B = image[0::2, 0::2]
            G0 = image[0::2, 1::2]
            G1 = image[1::2, 0::2]

        else:
            self.log.info('Unknown debayer pattern, keep it')
            return image

        image = 0.2989 * R + 0.5870 * (G0 + G1) / 2 + 0.1140 * B
        image = np.array(Image.fromarray(image).resize((h, w)))
        return image

    def writeHeaderDataToGUI(self, header):
        """
        :param header:
        :return: True for test purpose
        """
        self.guiSetText(self.ui.object, 's', header.get('OBJECT', '').upper())
        ra, dec = getCoordinates(header=header)
        self.guiSetText(self.ui.ra, 'HSTR', ra)
        self.guiSetText(self.ui.dec, 'DSTR', dec)
        self.guiSetText(self.ui.scale, '5.3f', getScale(header=header))
        self.guiSetText(self.ui.rotation, '6.3f', header.get('ANGLE'))
        self.guiSetText(self.ui.ccdTemp, '4.1f', header.get('CCD-TEMP'))
        self.guiSetText(self.ui.expTime, '5.1f', getExposure(header=header))
        self.guiSetText(self.ui.filter, 's', header.get('FILTER'))
        self.guiSetText(self.ui.binX, '1.0f', header.get('XBINNING'))
        self.guiSetText(self.ui.binY, '1.0f', header.get('YBINNING'))
        self.guiSetText(self.ui.sqm, '5.2f', getSQM(header=header))
        return True

    @staticmethod
    def checkFormatImage(image):
        """
        :param image:
        :return:
        """
        image = np.flipud(image)
        image = image / np.max(image) * 65536.0
        return image.astype('float32')

    def workerLoadImage(self):
        """
        :return:
        """
        with fits.open(self.imageFileName, mode='update') as fitsHandle:
            self.image = fitsHandle[0].data
            self.header = fitsHandle[0].header

        if self.image is None or len(self.image) == 0:
            self.log.debug('No image data in FITS')
            return False
        if self.header is None:
            self.log.debug('No header data in FITS')
            return False

        self.image = self.checkFormatImage(self.image)
        bayerPattern = self.header.get('BAYERPAT', '')
        if bayerPattern:
            self.image = self.debayerImage(self.image, bayerPattern)
            self.log.debug(f'Image has bayer pattern: {bayerPattern}')

        self.updateWindowsStats()
        self.writeHeaderDataToGUI(self.header)
        self.stackImages()
        return True

    def showImage(self, imagePath=''):
        """
        :param: imagePath:
        :return:
        """
        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        if not self.deviceStat['exposeN']:
            self.clearGui()

        self.changeStyleDynamic(self.ui.headerGroup, 'running', True)
        self.imageFileName = imagePath
        worker = Worker(self.workerLoadImage)
        worker.signals.finished.connect(self.preparePhotometry)
        self.threadPool.start(worker)
        return True

    def showCurrent(self):
        """
        :return: true for test purpose
        """
        self.showImage(self.imageFileName)
        return True

    def exposeRaw(self):
        """
        :return: True for test purpose
        """
        subFrame = self.app.camera.subFrame
        fastReadout = self.app.camera.fastDownload

        time = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        fileName = time + '-exposure.fits'
        imagePath = self.app.mwGlob['imageDir'] + '/' + fileName
        focalLength = self.app.telescope.focalLength

        self.imageFileNameOld = self.imageFileName
        suc = self.app.camera.expose(imagePath=imagePath,
                                     expTime=self.expTime,
                                     binning=self.binning,
                                     subFrame=subFrame,
                                     fastReadout=fastReadout,
                                     focalLength=focalLength
                                     )
        if not suc:
            text = f'Cannot expose:       [{os.path.basename(imagePath)}]'
            self.abortImage()
            self.app.message.emit(text, 2)
            return False

        text = f'Exposing:            [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)
        text = f'Duration:{self.expTime:3.0f}s  '
        text += f'Bin:{self.binning:1.0f}  Sub:{subFrame:3.0f}%'
        self.app.message.emit(f'                     {text}', 0)
        return True

    def exposeImageDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        self.deviceStat['expose'] = False
        self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        text = f'Exposed:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)

        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        self.app.showImage.emit(imagePath)
        return True

    def exposeImage(self):
        """
        :return: success
        """
        self.expTime = self.app.camera.expTime
        self.binning = int(self.app.camera.binning)
        self.imageStack = None
        self.deviceStat['expose'] = True
        self.ui.stackImages.setChecked(False)
        self.app.camera.signals.saved.connect(self.exposeImageDone)
        self.exposeRaw()
        return True

    def exposeImageNDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        text = f'Exposed:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)

        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        self.app.showImage.emit(imagePath)
        self.exposeRaw()
        return True

    def exposeImageN(self):
        """
        :return: success
        """
        self.expTime = self.app.camera.expTimeN
        self.binning = int(self.app.camera.binningN)
        self.imageStack = None
        self.deviceStat['exposeN'] = True
        self.app.camera.signals.saved.connect(self.exposeImageNDone)
        self.exposeRaw()
        return True

    def abortImage(self):
        """
        :return: True for test purpose
        """
        self.app.camera.abort()
        # for disconnection we have to split which slots were connected to
        # disable the right ones
        if self.deviceStat['expose']:
            self.app.camera.signals.saved.disconnect(self.exposeImageDone)

        if self.deviceStat['exposeN']:
            self.app.camera.signals.saved.disconnect(self.exposeImageNDone)

        # last image file was not stored, so getting last valid it back
        self.imageFileName = self.imageFileNameOld
        self.deviceStat['expose'] = False
        self.deviceStat['exposeN'] = False
        self.app.message.emit('Exposing aborted', 2)
        return True

    def solveDone(self, result=None):
        """
        :param result: result (named tuple)
        :return: success
        """
        self.deviceStat['solve'] = False
        self.app.astrometry.signals.done.disconnect(self.solveDone)

        if not result:
            self.app.message.emit('Solving error, result missing', 2)
            return False

        if result['success']:
            text = 'Solved :             '
            text += f'RA: {convertToHMS(result["raJ2000S"])} '
            text += f'({result["raJ2000S"].hours:4.3f}), '
            text += f'DEC: {convertToDMS(result["decJ2000S"])} '
            text += f'({result["decJ2000S"].degrees:4.3f}), '
            self.app.message.emit(text, 0)
            text = '                     '
            text += f'Angle: {result["angleS"]:3.0f}, '
            text += f'Scale: {result["scaleS"]:4.3f}, '
            text += f'Error: {result["errorRMS_S"]:4.1f}'
            self.app.message.emit(text, 0)
            if self.ui.embedData.isChecked():
                self.showCurrent()

        else:
            text = f'Solving error:       {result.get("message")}'
            self.app.message.emit(text, 2)
            return False

        return True

    def solveImage(self, imagePath=''):
        """
        :param imagePath:
        :return:
        """
        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        updateFits = self.ui.embedData.isChecked()
        self.app.astrometry.signals.done.connect(self.solveDone)
        self.app.astrometry.solveThreading(fitsPath=imagePath,
                                           updateFits=updateFits)
        self.deviceStat['solve'] = True
        text = f'Solving:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)
        return True

    def solveCurrent(self):
        """
        :return: true for test purpose
        """
        self.signals.solveImage.emit(self.imageFileName)
        return True

    def abortSolve(self):
        """
        :return: success
        """
        suc = self.app.astrometry.abort()
        return suc
