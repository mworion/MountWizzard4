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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import time
import gzip
import shutil

# external packages
from PyQt5.QtCore import Qt, pyqtSignal
import requests

# local import
from gui.utilities import toolsQtWidget
from base.tpool import Worker
from gui.widgets.downloadPopup_ui import Ui_DownloadPopup


class ProgressPopup(toolsQtWidget.MWidget):
    """
    """

    __all__ = ['ProgressPopup',
               ]

    signalProgress = pyqtSignal(object)

    def __init__(self,
                 parentWidget,
                 title='',
                 callBack=None,
                 ):

        super().__init__()
        self.ui = Ui_DownloadPopup()
        self.ui.setupUi(self)
        self.initUI()
        self.callBack = callBack
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)
        self.signalProgress.connect(self.setProgressBarToValue)
        self.show()

    def setProgressBarToValue(self, progressPercent):
        """
        :param progressPercent:
        :return: True for test purpose
        """
        self.ui.progressBar.setValue(progressPercent)
        return True
