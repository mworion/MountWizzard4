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
import logging
import json

# external packages
import matplotlib.pyplot as plt
import numpy as np

# local import
from mw4.base.loggerMW import CustomLogger
from mw4.gui import widget
from mw4.gui.widgets import analyse_ui


class AnalyseWindow(widget.MWidget):
    """
    the analyse window class handles

    """

    __all__ = ['AnalyseWindow',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.ui = analyse_ui.Ui_AnalyseDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.raPointErrors = self.embedMatplot(self.ui.raPointErrors,
                                               constrainedLayout=False)
        self.raPointErrors.parentWidget().setStyleSheet(self.BACK_BG)
        self.decPointErrors = self.embedMatplot(self.ui.decPointErrors,
                                                constrainedLayout=False)
        self.decPointErrors.parentWidget().setStyleSheet(self.BACK_BG)
        self.raModelErrors = self.embedMatplot(self.ui.raModelErrors,
                                               constrainedLayout=False)
        self.raModelErrors.parentWidget().setStyleSheet(self.BACK_BG)
        self.decModelErrors = self.embedMatplot(self.ui.decModelErrors,
                                                constrainedLayout=False)
        self.decModelErrors.parentWidget().setStyleSheet(self.BACK_BG)
        self.scaleImage = self.embedMatplot(self.ui.scaleImage,
                                            constrainedLayout=False)
        self.scaleImage.parentWidget().setStyleSheet(self.BACK_BG)
        self.modelPositions = self.embedMatplot(self.ui.modelPositions,
                                                constrainedLayout=False)
        self.modelPositions.parentWidget().setStyleSheet(self.BACK_BG)
        self.errorAscending = self.embedMatplot(self.ui.errorAscending,
                                                constrainedLayout=False)
        self.errorAscending.parentWidget().setStyleSheet(self.BACK_BG)
        self.errorDistribution = self.embedMatplot(self.ui.errorDistribution,
                                                   constrainedLayout=False)
        self.errorDistribution.parentWidget().setStyleSheet(self.BACK_BG)

        self.ui.load.clicked.connect(self.loadModel)
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

        if not isinstance(loadFilePath, str):
            return False

        with open(loadFilePath, 'r') as infile:
            modelJSON = json.load(infile)

        print(modelJSON)

        return True

    def draw_raPointErrors(self):
        pass

    def draw_decPointErrors(self):
        pass

    def draw_raModelErrors(self):
        pass

    def draw_decModelErrors(self):
        pass

    def draw_scaleImage(self):
        pass

    def draw_modelPositions(self):
        pass

    def draw_errorAscending(self):
        pass

    def draw_errorDistribution(self):
        pass

    def drawAll(self):
        """

        :return: true for test purpose
        """

        self.draw_raPointErrors()
        self.draw_decPointErrors()
        self.draw_raModelErrors()
        self.draw_decModelErrors()
        self.draw_scaleImage()
        self.draw_modelPositions()
        self.draw_errorAscending()
        self.draw_errorDistribution()

        return True
