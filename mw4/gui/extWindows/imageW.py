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
import PyQt5.QtWidgets
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter
from astropy.io import fits
from astropy import wcs
from astropy.nddata import Cutout2D
from astropy.visualization import MinMaxInterval
from astropy.visualization import AsinhStretch
from astropy.visualization import imshow_norm
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
import sep
from PIL import Image

# local import
from mountcontrol.convert import convertToDMS, convertToHMS
from base.fitsHeader import getCoordinates, getSQM, getExposure, getScale
from gui.utilities import toolsQtWidget
from gui.widgets import image_ui
from base.tpool import Worker


class ImageWindowSignals(PyQt5.QtCore.QObject):
    """
    """
    __all__ = ['ImageWindowSignals']
    solveImage = PyQt5.QtCore.pyqtSignal(object)


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

        self.imageFileName = ''
        self.imageFileNameOld = ''
        self.expTime = 1
        self.binning = 1
        self.image = None
        self.folder = ''
        self.header = None
        self.imageStack = None
        self.numberStack = 0
        self.colorMap = None
        self.stretch = None
        self.objs = None
        self.bk_back = None
        self.bk_rms = None
        self.flux = None
        self.radius = None

        self.deviceStat = {
            'expose': False,
            'exposeN': False,
            'solve': False,
        }
        self.view = {0: 'Image Raw',
                     1: 'Image with Sources',
                     2: 'Photometry: HFD value',
                     3: 'Photometry: Eccentricity',
                     4: 'Photometry: Background level',
                     5: 'Photometry: Background noise',
                     6: 'Photometry: Flux',
                     7: 'Photometry: HFD Contour',
                     }

        self.colorMaps = {'Grey': 'gray',
                          'Cool': 'plasma',
                          'Rainbow': 'rainbow',
                          'Spectral': 'nipy_spectral',
                          }

        self.stretchValues = {'Low XX': 0.2,
                              'Low X': 0.1,
                              'Low': 0.05,
                              'Mid': 0.025,
                              'High': 0.005,
                              'Super ': 0.0025,
                              'Super X': 0.001,
                              'Super XX': 0.0005,
                              }

        self.zoomLevel = {' 1x Zoom': 1,
                          ' 2x Zoom': 2,
                          ' 4x Zoom': 4,
                          ' 8x Zoom': 8,
                          '16x Zoom': 16,
                          }

        self.imageMat = self.embedMatplot(self.ui.image, constrainedLayout=False)
        # self.imageMat.parentWidget().setStyleSheet(self.BACK_BG)
        self.fig = self.imageMat.figure
        self.axe = None
        self.axeCB = None

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

        self.setupDropDownGui()
        self.ui.color.setCurrentIndex(config.get('color', 0))
        self.ui.zoom.setCurrentIndex(config.get('zoom', 0))
        self.ui.view.setCurrentIndex(config.get('view', 0))
        self.ui.stretch.setCurrentIndex(config.get('stretch', 0))
        self.imageFileName = config.get('imageFileName', '')
        self.folder = self.app.mwGlob.get('imageDir', '')
        self.ui.checkStackImages.setChecked(config.get('checkStackImages', False))
        self.ui.checkShowCrosshair.setChecked(config.get('checkShowCrosshair', False))
        self.ui.checkShowGrid.setChecked(config.get('checkShowGrid', True))
        self.ui.checkAutoSolve.setChecked(config.get('checkAutoSolve', False))
        self.ui.checkEmbedData.setChecked(config.get('checkEmbedData', False))
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
        config['zoom'] = self.ui.zoom.currentIndex()
        config['view'] = self.ui.view.currentIndex()
        config['stretch'] = self.ui.stretch.currentIndex()
        config['imageFileName'] = self.imageFileName
        config['checkStackImages'] = self.ui.checkStackImages.isChecked()
        config['checkShowCrosshair'] = self.ui.checkShowCrosshair.isChecked()
        config['checkShowGrid'] = self.ui.checkShowGrid.isChecked()
        config['checkAutoSolve'] = self.ui.checkAutoSolve.isChecked()
        config['checkEmbedData'] = self.ui.checkEmbedData.isChecked()
        return True

    def showWindow(self):
        """
        showWindow prepares all data for showing the window, plots the image and
        show it. afterwards all necessary signal / slot connections will be
        established.

        :return: true for test purpose
        """
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.preparePlot)
        self.ui.stretch.currentIndexChanged.connect(self.preparePlot)
        self.ui.zoom.currentIndexChanged.connect(self.showCurrent)
        self.ui.view.currentIndexChanged.connect(self.preparePlot)
        self.ui.checkShowGrid.clicked.connect(self.preparePlot)
        self.ui.checkShowCrosshair.clicked.connect(self.preparePlot)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.checkStackImages.clicked.connect(self.clearStack)
        self.ui.abortImage.clicked.connect(self.abortImage)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.signals.solveImage.connect(self.solveImage)
        self.app.showImage.connect(self.showImage)
        self.app.colorChange.connect(self.colorChange)
        self.show()
        self.showCurrent()
        return True

    def closeEvent(self, closeEvent):
        """
        closeEvent overlays the window close event of qt. first it stores all
        persistent data for the windows and its functions, than removes al signal
        / slot connections removes the matplotlib embedding and finally calls the
        parent calls for handling the framework close event.

        :param closeEvent:
        :return: True for test purpose
        """
        self.storeConfig()
        self.ui.load.clicked.disconnect(self.selectImage)
        self.ui.color.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.stretch.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.zoom.currentIndexChanged.disconnect(self.showCurrent)
        self.ui.view.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.checkShowGrid.clicked.disconnect(self.preparePlot)
        self.ui.checkShowCrosshair.clicked.disconnect(self.preparePlot)
        self.ui.solve.clicked.disconnect(self.solveCurrent)
        self.ui.expose.clicked.disconnect(self.exposeImage)
        self.ui.exposeN.clicked.disconnect(self.exposeImageN)
        self.ui.checkStackImages.clicked.disconnect(self.clearStack)
        self.ui.abortImage.clicked.disconnect(self.abortImage)
        self.ui.abortSolve.clicked.disconnect(self.abortSolve)
        self.signals.solveImage.disconnect(self.solveImage)
        self.app.showImage.disconnect(self.showImage)
        self.app.colorChange.disconnect(self.colorChange)
        super().closeEvent(closeEvent)

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.showCurrent()
        return True

    def setupDropDownGui(self):
        """
        :return: success for test
        """
        self.ui.color.clear()
        self.ui.color.setView(PyQt5.QtWidgets.QListView())
        for text in self.colorMaps:
            self.ui.color.addItem(text)

        self.ui.zoom.clear()
        self.ui.zoom.setView(PyQt5.QtWidgets.QListView())
        for text in self.zoomLevel:
            self.ui.zoom.addItem(text)

        self.ui.stretch.clear()
        self.ui.stretch.setView(PyQt5.QtWidgets.QListView())
        for text in self.stretchValues:
            self.ui.stretch.addItem(text)

        self.ui.view.clear()
        self.ui.view.setView(PyQt5.QtWidgets.QListView())
        for menuNumber in self.view:
            self.ui.view.addItem(self.view[menuNumber])

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

        self.ui.imageFileName.setText(name)
        self.imageFileName = loadFilePath
        self.app.message.emit(f'Image selected:      [{name}]', 0)
        self.folder = os.path.dirname(loadFilePath)
        if self.ui.checkAutoSolve.isChecked():
            self.signals.solveImage.emit(self.imageFileName)
        self.app.showImage.emit(self.imageFileName)
        return True

    def setupNormal(self):
        """
        :return: True for test purpose
        """
        self.fig.clf()
        self.axe = self.fig.add_subplot(1, 1, 1,
                                        facecolor=self.M_BACK)

        self.fig.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.85)
        self.axeCB = self.fig.add_axes([0.88, 0.1, 0.02, 0.8])
        self.axe.spines['bottom'].set_color(self.M_BLUE)
        self.axe.spines['top'].set_color(self.M_BLUE)
        self.axe.spines['left'].set_color(self.M_BLUE)
        self.axe.spines['right'].set_color(self.M_BLUE)

        factor = self.zoomLevel[self.ui.zoom.currentText()]
        sizeX = self.header.get('NAXIS1', 1) / factor
        sizeY = self.header.get('NAXIS2', 1) / factor
        midX = int(sizeX / 2)
        midY = int(sizeY / 2)
        number = 10

        if self.ui.checkShowCrosshair.isChecked():
            self.axe.axvline(midX, color=self.M_RED)
            self.axe.axhline(midY, color=self.M_RED)

        if self.ui.checkShowGrid.isChecked():
            self.axe.grid(True, color=self.M_GREY, ls='solid', alpha=1)

        self.axe.tick_params(axis='x', which='major',
                             colors=self.M_BLUE, labelsize=12)
        self.axe.tick_params(axis='y', which='major',
                             colors=self.M_BLUE, labelsize=12)

        valueX, _ = np.linspace(-midX, midX, num=number, retstep=True)
        textX = list((str(int(x)) for x in valueX))
        ticksX = list((x + midX for x in valueX))
        self.axe.set_xticks(ticksX)
        self.axe.set_xticklabels(textX)

        valueY, _ = np.linspace(-midY, midY, num=number, retstep=True)
        textY = list((str(int(x)) for x in valueY))
        ticksY = list((x + midY for x in valueY))
        self.axe.set_yticks(ticksY)
        self.axe.set_yticklabels(textY)

        self.axe.set_xlabel(xlabel='Pixel', color=self.M_BLUE,
                            fontsize=12, fontweight='bold')
        self.axe.set_ylabel(ylabel='Pixel', color=self.M_BLUE,
                            fontsize=12, fontweight='bold')

        self.axe.set_xlim(0, sizeX)
        self.axe.set_ylim(0, sizeY)
        return True

    def colorImage(self):
        """
        :return: True
        """
        fallback = list(self.colorMaps.keys())[0]
        self.colorMap = self.colorMaps.get(self.ui.color.currentText(), fallback)
        return True

    def stretchImage(self):
        """
        :return: True
        """
        fallback = list(self.stretchValues.keys())[0]
        value = self.stretchValues.get(self.ui.stretch.currentText(),
                                       self.stretchValues[fallback])
        self.stretch = AsinhStretch(a=value)
        return True

    def imageRawPlot(self, imageDisp=None):
        """
        :return:
        """
        img = imshow_norm(imageDisp,
                          ax=self.axe,
                          origin='lower',
                          interval=MinMaxInterval(),
                          stretch=self.stretch,
                          cmap=self.colorMap,
                          aspect='auto')
        return img

    def imagePlot(self):
        """
        :return:
        """
        if self.ui.view.currentIndex() == 0:
            img = self.imageRawPlot(imageDisp=self.image)
            self.log.debug('Show 0')

            if self.axeCB:
                colorbar = self.fig.colorbar(img[0], cax=self.axeCB)
                colorbar.set_label('Value [pixel value]',
                                   color=self.M_BLUE,
                                   fontsize=12)
                yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
                plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 1:
            if self.objs is None:
                self.log.debug('Show 1, no SEP data')
                return False

            self.imageRawPlot(imageDisp=self.image)
            for i in range(len(self.objs)):
                e = Ellipse(xy=(self.objs['x'][i], self.objs['y'][i]),
                            width=6 * self.objs['a'][i],
                            height=6 * self.objs['b'][i],
                            angle=self.objs['theta'][i] * 180. / np.pi)
                e.set_facecolor('none')
                e.set_edgecolor(self.M_BLUE)
                self.axe.add_artist(e)

            if self.axeCB:
                self.axeCB.axis('off')

        if self.ui.view.currentIndex() == 2:
            if self.objs is None or self.radius is None:
                self.log.debug('Show 2, no SEP radius data')
                return False

            self.imageRawPlot(imageDisp=self.image)
            draw = self.radius.argsort()[-50:][::-1]
            for i in draw:
                e = Ellipse(xy=(self.objs['x'][i], self.objs['y'][i]),
                            width=6 * self.objs['a'][i],
                            height=6 * self.objs['b'][i],
                            angle=self.objs['theta'][i] * 180.0 / np.pi)
                e.set_facecolor('none')
                e.set_edgecolor(self.M_BLUE)
                self.axe.add_artist(e)
                posX = self.objs['x'][i] + self.objs['a'][i] + 5
                posY = self.objs['b'][i] + self.objs['y'][i] + 5
                self.axe.annotate(f'{self.radius[i]:2.1f}',
                                  xy=(posX, posY),
                                  color=self.M_BLUE,
                                  fontweight='bold')
            if self.axeCB:
                self.axeCB.axis('off')

        if self.ui.view.currentIndex() == 3:
            if self.objs is None:
                self.log.debug('Show 3, no SEP data')
                return False

            self.imageRawPlot(imageDisp=self.image)
            a = self.objs['a']
            b = self.objs['b']
            eccentricity = np.sqrt(1 - b ** 2 / a ** 2)
            area = 5
            scatter = self.axe.scatter(self.objs['x'], self.objs['y'],
                                       c=eccentricity, s=area, cmap='gnuplot2')

            colorbar = self.fig.colorbar(scatter, cax=self.axeCB)
            colorbar.set_label('Eccentricity []', color=self.M_BLUE,
                               fontsize=12)
            yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
            plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 4:
            if self.bk_back is None:
                self.log.debug('Show 4, no SEP background data')
                return False

            img = self.imageRawPlot(imageDisp=self.bk_back)
            if self.axeCB:
                colorbar = self.fig.colorbar(img[0], cax=self.axeCB)
                colorbar.set_label('Background level [adu]',
                                   color=self.M_BLUE,
                                   fontsize=12)
                yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
                plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 5:
            if self.bk_rms is None:
                self.log.debug('Show 5, no SEP background rms data')
                return False

            img = self.imageRawPlot(imageDisp=self.bk_rms)
            if self.axeCB:
                colorbar = self.fig.colorbar(img[0], cax=self.axeCB)
                colorbar.set_label('Background noise [adu]',
                                   color=self.M_BLUE,
                                   fontsize=12)
                yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
                plt.setp(yTicks, color=self.M_BLUE,
                         fontweight='bold')

        if self.ui.view.currentIndex() == 6:
            if self.flux is None or self.objs is None:
                self.log.debug('Show 5, no SEP flux data')
                return False

            flux = np.log(self.flux)
            area = 3 * flux
            scatter = self.axe.scatter(self.objs['x'], self.objs['y'],
                                       c=flux, s=area, cmap=self.colorMap)

            colorbar = self.fig.colorbar(scatter, cax=self.axeCB)
            colorbar.set_label('Flux [log(x)]', color=self.M_BLUE, fontsize=12)
            yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
            plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 7:
            if self.radius is None or self.objs is None:
                self.log.debug('Show 7, no SEP radius data')
                return False

            x = self.objs['x']
            y = self.objs['y']
            z = self.radius
            width = self.image.shape[1]
            height = self.image.shape[0]
            X, Y = np.meshgrid(range(0, width, int(width / 250)),
                               range(0, height, int(height / 250)))
            Z = griddata((x, y), z, (X, Y), method='linear', fill_value=np.mean(z))
            Z = uniform_filter(Z, size=25)
            self.axe.contourf(X, Y, Z, 20)
            if self.axeCB:
                self.axeCB.axis('off')

        self.axe.figure.canvas.draw()
        return True

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
        flipped = bool(header.get('FLIPPED', False))
        self.ui.isFlipped.setEnabled(flipped)
        return True

    def workerPreparePlot(self):
        """
        :return:
        """
        self.updateWindowsStats()
        self.setupNormal()
        self.writeHeaderDataToGUI(self.header)
        self.stretchImage()
        self.colorImage()
        suc = self.imagePlot()
        if not suc:
            t = 'Image type could not be shown - display raw image'
            self.app.message.emit(t, 2)
            self.ui.view.setCurrentIndex(0)
        return suc

    def preparePlot(self):
        """
        :return:
        """
        worker = Worker(self.workerPreparePlot)
        self.threadPool.start(worker)
        return True

    def workerPreparePhotometry(self):
        """
        :return:
        """
        bkg = sep.Background(self.image)
        self.bk_back = bkg.back()
        self.bk_rms = bkg.rms()
        image_sub = self.image - bkg
        self.objs = sep.extract(image_sub, 1.5, err=bkg.globalrms,
                                filter_type='conv',
                                minarea=10)
        self.flux, _, _ = sep.sum_circle(image_sub,
                                         self.objs['x'],
                                         self.objs['y'],
                                         3.0,
                                         err=bkg.globalrms,
                                         gain=1.0)
        self.radius, _ = sep.flux_radius(image_sub,
                                         self.objs['x'],
                                         self.objs['y'],
                                         6.0 * self.objs['a'],
                                         0.5,
                                         normflux=self.flux,
                                         subpix=5)
        return True

    def preparePhotometry(self):
        """
        :return:
        """
        if self.objs is None:
            worker = Worker(self.workerPreparePhotometry)
            worker.signals.finished.connect(self.preparePlot)
            self.threadPool.start(worker)
        else:
            self.preparePlot()
        return True

    def stackImages(self):
        """
        :return:
        """
        if not self.ui.checkStackImages.isChecked():
            self.imageStack = None
            self.ui.numberStacks.setText('single')
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
        self.ui.numberStacks.setText(f'mean of: {self.numberStack:4.0f}')
        return True

    def clearStack(self):
        """
        :return:
        """
        if not self.ui.checkStackImages.isChecked():
            self.imageStack = None
            self.numberStack = 0
            self.ui.numberStacks.setText('single')
            return False

        return True

    def zoomImage(self):
        """
        :return: true
        """
        sizeY, sizeX = self.image.shape
        fallback = list(self.zoomLevel.keys())[0]
        factor = self.zoomLevel.get(self.ui.zoom.currentText(), fallback)
        if factor == 1:
            return

        position = (int(sizeX / 2), int(sizeY / 2))
        size = (int(sizeY / factor), int(sizeX / factor))
        self.log.debug(f'Image zoomed to position:[{position}], size:[{size}]')
        self.image = Cutout2D(self.image,
                              position=position,
                              size=size,
                              wcs=wcs.WCS(self.header, relax=True),
                              copy=True).data
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

    def workerLoadImage(self):
        """
        :return:
        """
        full, short, ext = self.extractNames([self.imageFileName])
        self.ui.imageFileName.setText(short)

        with fits.open(self.imageFileName, mode='update') as fitsHandle:
            self.image = fitsHandle[0].data
            self.header = fitsHandle[0].header

        if self.image is None or len(self.image) == 0:
            self.log.debug('No image data in FITS')
            return False
        if self.header is None:
            self.log.debug('No header data in FITS')
            return False

        self.image = np.flipud(self.image).astype('float32')
        bayerPattern = self.header.get('BAYERPAT', '')
        if bayerPattern:
            self.image = self.debayerImage(self.image, bayerPattern)
            self.log.debug(f'Image has bayer pattern: {bayerPattern}')

        self.zoomImage()
        self.stackImages()
        self.objs = None
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

        self.ui.loading.setText('Loading....')
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
        fastReadout = self.app.camera.checkFastDownload

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

        if self.ui.checkAutoSolve.isChecked():
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
        self.ui.checkStackImages.setChecked(False)
        self.app.camera.signals.saved.connect(self.exposeImageDone)
        self.ui.numberStacks.setText('...')
        self.exposeRaw()
        return True

    def exposeImageNDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        text = f'Exposed:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)

        if self.ui.checkAutoSolve.isChecked():
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
        self.ui.numberStacks.setText('...')
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

        updateFits = self.ui.checkEmbedData.isChecked()
        self.app.astrometry.signals.done.connect(self.solveDone)
        self.app.astrometry.solveThreading(fitsPath=imagePath,
                                           updateFits=updateFits,
                                           )
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
