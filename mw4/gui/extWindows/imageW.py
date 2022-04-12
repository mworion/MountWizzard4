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
        self.ui.tilt.setColorMap(colorMap)
        self.ui.roundness.setColorMap(colorMap)
        self.ui.aberation.setColorMap(colorMap)
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
        self.ui.background.p[0].setAspectLocked(isLocked)
        self.ui.backgroundRMS.p[0].setAspectLocked(isLocked)
        self.ui.hfd.p[0].setAspectLocked(isLocked)
        self.ui.tilt.p[0].setAspectLocked(isLocked)
        self.ui.roundness.p[0].setAspectLocked(isLocked)
        return True

    @staticmethod
    def calcAberationInspectView(img):
        """
        :param img:
        :return:
        """
        size = 250
        h, w = img.shape
        if w < 3 * size or h < 3 * size:
            return img

        dw = int((w - 3 * size) / 2)
        dh = int((h - 3 * size) / 2)

        img = np.delete(img, np.s_[size:size + dh], axis=0)
        img = np.delete(img, np.s_[size * 2:size * 2 + dh], axis=0)
        img = np.delete(img, np.s_[size:size + dw], axis=1)
        img = np.delete(img, np.s_[size * 2:size * 2 + dw], axis=1)

        img[size - 2:size + 2, :] = 0
        img[2 * size - 2:2 * size + 2, :] = 0
        img[:, size - 2:size + 2] = 0
        img[:, 2 * size - 2:2 * size + 2] = 0

        return img

    def setImage(self):
        """
        :return:
        """
        self.setBarColor()
        self.ui.image.setImage(imageDisp=self.image)
        self.setCrosshair()
        QApplication.processEvents()
        if self.HFD is None:
            return False

        # base calculations
        scale = 5
        ys, xs = self.image.shape
        rangeX = np.linspace(0, xs, int(xs / scale))
        rangeY = np.linspace(0, ys, int(ys / scale))
        xm, ym = np.meshgrid(rangeX, rangeY)
        filterConst = int(xs / scale / 2)
        medianHFD = np.median(self.HFD)
        self.ui.medianHFD.setText(f'{medianHFD:1.1f}')
        self.ui.numberStars.setText(f'{len(self.HFD):1.0f}')

        # background
        self.ui.tabImage.setTabEnabled(1, True)
        QApplication.processEvents()
        back = self.bkg.back()
        maxB = np.max(back) / self.bkg.globalback
        minB = np.min(back) / self.bkg.globalback
        img = self.bkg.back() / self.bkg.globalback
        img = uniform_filter(img, size=filterConst)
        self.ui.background.setImage(imageDisp=img)
        self.ui.background.barItem.setLevels((minB, maxB))

        # hfd values
        self.ui.tabImage.setTabEnabled(2, True)
        QApplication.processEvents()
        img = griddata((self.objs['x'], self.objs['y']), self.HFD, (xm, ym),
                       method='nearest', fill_value=np.min(self.HFD))
        img = uniform_filter(img, size=filterConst)
        self.ui.hfd.setImage(imageDisp=img)
        hfdPercentile10 = np.percentile(self.HFD, 90)
        self.ui.hfdPercentile.setText(f'{hfdPercentile10:1.1f}')
        self.ui.hfd.p[0].getAxis('left').setScale(scale=scale)
        self.ui.hfd.p[0].getAxis('bottom').setScale(scale=scale)

        # tilt values
        self.ui.tabImage.setTabEnabled(3, True)
        QApplication.processEvents()
        self.ui.tilt.setImage(imageDisp=img)
        self.ui.tilt.p[0].getAxis('left').setScale(scale=scale)
        self.ui.tilt.p[0].getAxis('bottom').setScale(scale=scale)

        # roundness as image
        self.ui.tabImage.setTabEnabled(4, True)
        QApplication.processEvents()
        a = self.objs['a']
        b = self.objs['b']
        aspectRatio = np.maximum(a/b, b/a)
        minB, maxB = np.percentile(aspectRatio, (50, 95))
        img = griddata((self.objs['x'], self.objs['y']), aspectRatio, (xm, ym),
                       method='linear', fill_value=np.min(aspectRatio))
        img = uniform_filter(img, size=filterConst)
        self.ui.roundness.setImage(imageDisp=img)
        self.ui.roundness.barItem.setLevels((minB, maxB))
        aspectRatioPercentile10 = np.percentile(aspectRatio, 90)
        self.ui.aspectRatioPercentile.setText(f'{aspectRatioPercentile10:1.1f}')
        self.ui.roundness.p[0].getAxis('left').setScale(scale=scale)
        self.ui.roundness.p[0].getAxis('bottom').setScale(scale=scale)

        # aberation inspection
        self.ui.tabImage.setTabEnabled(5, True)
        QApplication.processEvents()
        self.ui.aberation.p[0].setAspectLocked(True)
        abb = self.calcAberationInspectView(self.image)
        self.ui.aberation.setImage(abb)
        self.ui.aberation.p[0].getViewBox().setMouseMode(pg.ViewBox().PanMode)
        self.ui.aberation.p[0].showAxes(False, showValues=False)
        self.ui.aberation.p[0].setMouseEnabled(x=False, y=False)
        self.ui.aberation.p[0].getViewBox().rightMouseRange()

        # image with detected sources
        self.ui.tabImage.setTabEnabled(6, True)
        QApplication.processEvents()
        self.ui.imageSource.setImage(imageDisp=self.image)
        for i in range(len(self.objs)):
            self.ui.imageSource.addEllipse(self.objs['x'][i], self.objs['y'][i],
                                           self.objs['a'][i], self.objs['b'][i],
                                           self.objs['theta'][i])

        # background rms
        self.ui.tabImage.setTabEnabled(7, True)
        QApplication.processEvents()
        img = self.bkg.rms()
        img = uniform_filter(img, size=filterConst)
        self.ui.backgroundRMS.setImage(imageDisp=img)
        return True

    def workerPreparePhotometry(self):
        """
        :return:
        """
        self.bkg = sep.Background(self.image, fthresh=np.median(self.image))
        image_sub = self.image - self.bkg
        obj = sep.extract(
            image_sub, 2.5, err=self.bkg.globalrms, filter_type='matched',
            minarea=14)

        # remove objects without need
        r = np.sqrt(obj['a'] * obj['a'] + obj['b'] * obj['b'])
        obj = obj[(r < 5) & (r > 1.25)]
        self.objs = obj

        kronRad, krFlag = sep.kron_radius(
            image_sub, obj['x'], obj['y'], obj['a'], obj['b'], obj['theta'], 6.0)

        flux, fluxErr, flag = sep.sum_ellipse(
            image_sub, obj['x'], obj['y'], obj['a'], obj['b'], obj['theta'],
            2.5 * kronRad, subpix=1)

        flag |= krFlag
        r_min = 1.75
        useCircle = kronRad * np.sqrt(obj['a'] * obj['b']) < r_min
        cFlux, cFluxErr, cFlag = sep.sum_circle(
            image_sub, obj['x'][useCircle], obj['y'][useCircle], r_min, subpix=1)

        flux[useCircle] = cFlux
        fluxErr[useCircle] = cFluxErr
        flag[useCircle] = cFlag

        radius, _ = sep.flux_radius(
            image_sub, obj['x'], obj['y'], 6.0 * obj['a'], 0.5,
            normflux=flux, subpix=5)

        # to get HFD
        self.HFD = 2 * radius
        self.image = self.image - self.bkg.back() * 0.5
        return True

    def preparePhotometry(self):
        """
        :return:
        """
        doPhotometry = self.ui.enablePhotometry.isChecked()
        if doPhotometry:
            worker = Worker(self.workerPreparePhotometry)
            worker.signals.finished.connect(self.setImage)
            self.threadPool.start(worker)
        else:
            self.objs = None
            self.bkg = None
            self.HFD = None
            self.setImage()
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
        if not image[0][0].dtype == np.dtype('float32'):
            image = np.flipud(image).astype('float32')
        else:
            image = np.flipud(image)

        image = image / np.max(image) * 65536
        return image

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

    def clearGui(self):
        """
        :return:
        """
        self.signals.showTitle.emit('')
        self.HFD = None
        self.ui.medianHFD.setText('')
        self.ui.hfdPercentile.setText('')
        self.ui.numberStars.setText('')
        self.ui.aspectRatioPercentile.setText('')
        for i in range(1, self.ui.tabImage.count()):
            self.ui.tabImage.setTabEnabled(i, False)
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
