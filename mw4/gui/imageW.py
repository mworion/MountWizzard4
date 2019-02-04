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
import logging
import os
# external packages
import PyQt5
from astropy.io import fits
from astropy.wcs import WCS
from astropy.visualization import MinMaxInterval
from astropy.visualization import SqrtStretch
from astropy.visualization import ImageNormalize
# local import
from mw4.gui import widget
from mw4.gui.widgets import image_ui


class ImageWindow(widget.MWidget):
    """
    the image window class handles

    """

    __all__ = ['ImageWindow',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    BACK = 'background-color: transparent;'
    CYCLE_UPDATE_TASK = 1000
    NUMBER_POINTS = 500
    NUMBER_XTICKS = 8

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.showStatus = False
        self.imageFileName = ''
        self.image = None

        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.setupDropDownGui()

        self.imageMat = self.embedMatplot(self.ui.image)
        self.imageMat.parentWidget().setStyleSheet(self.BACK)

        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.showFitsImage)

        self.initConfig()

    def initConfig(self):
        if 'imageW' not in self.app.config:
            return False
        config = self.app.config['imageW']
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
        if config.get('showStatus'):
            self.showWindow()
        self.ui.color.setCurrentIndex(config.get('color', 0))
        self.ui.zoom.setCurrentIndex(config.get('zoom', 0))
        self.ui.stretch.setCurrentIndex(config.get('stretch', 0))
        self.imageFileName = config.get('imageFileName', '')
        full, short, ext = self.extractNames([self.imageFileName])
        self.ui.imageFileName.setText(short)
        self.showFitsImage()
        return True

    def storeConfig(self):
        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
        config = self.app.config['imageW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['showStatus'] = self.showStatus
        config['color'] = self.ui.color.currentIndex()
        config['zoom'] = self.ui.zoom.currentIndex()
        config['stretch'] = self.ui.stretch.currentIndex()
        config['imageFileName'] = self.imageFileName
        return True

    def resizeEvent(self, QResizeEvent):
        """
        resizeEvent changes the internal widget according to the resize of the window
        the formulae of the calculation is:
            spaces left right top button : 5 pixel
            widget start in height at y = 130

        :param QResizeEvent:
        :return: nothing
        """

        super().resizeEvent(QResizeEvent)
        space = 5
        startY = 130
        self.ui.image.setGeometry(space,
                                  startY - space,
                                  self.width() - 2 * space,
                                  self.height() - startY)

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)
        self.changeStyleDynamic(self.app.mainW.ui.openImageW, 'running', 'false')

    def toggleWindow(self):
        self.showStatus = not self.showStatus
        if self.showStatus:
            self.showWindow()
        else:
            self.close()

    def showWindow(self):
        self.showStatus = True
        self.showFitsImage()
        self.show()
        self.changeStyleDynamic(self.app.mainW.ui.openImageW, 'running', 'true')
        return True

    def setupDropDownGui(self):
        """
        setupDropDownGui handles the population of list for image handling.

        :return: success for test
        """

        self.ui.color.clear()
        self.ui.color.setView(PyQt5.QtWidgets.QListView())
        self.ui.color.addItem('Grey')
        self.ui.color.addItem('Cool')
        self.ui.color.addItem('Rainbow')
        self.ui.color.addItem('Spectral')

        self.ui.zoom.clear()
        self.ui.zoom.setView(PyQt5.QtWidgets.QListView())
        self.ui.zoom.addItem('Zoom 1x')
        self.ui.zoom.addItem('Zoom 2x')
        self.ui.zoom.addItem('Zoom 4x')
        self.ui.zoom.addItem('Zoom 8x')

        self.ui.stretch.clear()
        self.ui.stretch.setView(PyQt5.QtWidgets.QListView())
        self.ui.stretch.addItem('Low')
        self.ui.stretch.addItem('Mid')
        self.ui.stretch.addItem('High')
        self.ui.stretch.addItem('Super')

        return True

    def selectImage(self):
        folder = self.app.mwGlob['imageDir']
        loadFilePath, name, ext = self.openFile(self,
                                                'Select image file',
                                                folder,
                                                'FITS files (*.fit*)',
                                                enableDir=True,
                                                )
        if not name:
            return False
        # suc = self.app.loadConfig(name=name)
        suc = True
        if suc:
            self.ui.imageFileName.setText(name)
            self.imageFileName = loadFilePath
            self.showFitsImage()
            self.app.message.emit('Image [{0}] loaded'.format(name), 0)
        else:
            self.app.message.emit('Image [{0}] cannot no be loaded'.format(name), 2)
        return True

    def showFitsImage(self):
        """

        :return:
        """

        if not self.showStatus:
            return False

        if not os.path.isfile(self.imageFileName):
            return False

        with fits.open(self.imageFileName) as fitsHandle:
            self.image = fitsHandle[0].data
            scale = fitsHandle[0].header.get('SCALE', 0)
            ra = fitsHandle[0].header.get('RA', 0)
            dec = fitsHandle[0].header.get('DEC', 0)
            ccdTemp = fitsHandle[0].header.get('CCD-TEMP', 0)
            wcs = WCS(fitsHandle[0].header)

        print(wcs.wcs.print_contents())

        self.ui.ra.setText(f'{ra:6.2f}')
        self.ui.dec.setText(f'{dec:6.2f}')
        self.ui.scale.setText(f'{scale:4.2f}')
        self.ui.ccdTemp.setText(f'{ccdTemp:4.1f}')

        colorMaps = ['gray', 'plasma', 'rainbow', 'nipy_spectral']
        colorMapIndex = self.ui.color.currentIndex()
        colorMap = colorMaps[colorMapIndex]
        color = '#2090C0'
        colorLeft = '#A0A0A0'
        colorRight = '#30B030'
        colorGrid = '#404040'

        self.imageMat.figure.clf()
        self.imageMat.figure.add_axes([0.1, 0.1, 0.8, 0.8],
                                      projection=wcs,
                                      )
        axes = self.imageMat.figure.axes[0]

        norm = ImageNormalize(self.image,
                              interval=MinMaxInterval(),
                              stretch=SqrtStretch())

        axes.imshow(self.image,
                    norm=norm,
                    cmap=colorMap,
                    zorder=-10,
                    origin='lower',
                    )
        axes.plot()
        axes.grid(True,
                  color=color,
                  ls='solid',
                  alpha=0.5,
                  )

        axes.tick_params(axis='x',
                         colors=color,
                         labelsize=12,
                         )

        axes.tick_params(axis='y',
                         colors=color,
                         labelsize=12,
                         labelleft=True,
                         )

        axes.set_xlabel('Galactic Longitude',
                        color=color,
                        )
        axes.set_ylabel('Galactic Latitude',
                        color=color,
                        )
        axes.set_title('WCS Test',
                       color=color,
                       )

        lon = axes.coords[0]
        lat = axes.coords[1]
        lon.set_major_formatter('dd:mm:ss.s')
        lat.set_major_formatter('dd:mm')
        lon.set_ticks_position('bt')
        lon.set_ticklabel_position('bt')
        lon.set_axislabel_position('bt')
        lat.set_ticks_position('lr')
        lat.set_ticklabel_position('lr')
        lat.set_axislabel_position('lr')
        axes.figure.canvas.draw()
        return

        '''


        overlay = axes.get_coords_overlay('fk5')
        overlay.grid(color=colorGrid,
                     ls='dotted',
                     )
        overlay[0].set_axislabel('Right Ascension (J2000)',
                                 color=color,
                                 fontweight='bold',
                                 fontsize=12)
        overlay[1].set_axislabel('Declination (J2000)',
                                 color=color,
                                 fontweight='bold',
                                 fontsize=12)
        '''

