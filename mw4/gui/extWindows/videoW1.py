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

# external packages
from PyQt5.QtCore import pyqtSignal

# local import
from gui.extWindows.videoW import VideoWindow


class VideoWindow1(VideoWindow):
    """
    the message window class handles
    """

    __all__ = ['VideoWindow1']

    pixmapReady = pyqtSignal(object)

    def __init__(self, app):
        super().__init__(app=app)
        self.setWindowTitle('Video Stream 1')
        self.setObjectName('Video1')

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'videoW1' not in self.app.config:
            self.app.config['videoW1'] = {}
        config = self.app.config['videoW1']
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
        self.ui.streamURL.setText(config.get('streamURL', ''))
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'videoW1' not in self.app.config:
            self.app.config['videoW1'] = {}
        config = self.app.config['videoW1']
        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        config['streamURL'] = self.ui.streamURL.text()
        return True
