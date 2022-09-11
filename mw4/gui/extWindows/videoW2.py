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


class VideoWindow2(VideoWindow):
    """
    the message window class handles
    """

    __all__ = ['VideoWindow2']
    pixmapReady = pyqtSignal(object)

    def __init__(self, app):
        super().__init__(app=app)
        self.setWindowTitle('Video Stream 2')
        self.setObjectName('Video2')

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'videoW2' not in self.app.config:
            self.app.config['videoW2'] = {}
        config = self.app.config['videoW2']

        self.positionWindow(config)
        self.ui.videoURL.setText(config.get('videoURL', ''))
        self.ui.videoSource.setCurrentIndex(config.get('videoSource', 0))
        self.ui.frameRate.setCurrentIndex(config.get('frameRate', 2))
        self.user = (config.get('user', ''))
        self.password = (config.get('password', ''))
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        if 'videoW2' not in config:
            config['videoW2'] = {}
        else:
            config['videoW2'].clear()
        config = config['videoW2']

        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        config['videoURL'] = self.ui.videoURL.text()
        config['videoSource'] = self.ui.videoSource.currentIndex()
        config['frameRate'] = self.ui.frameRate.currentIndex()
        config['user'] = self.user
        config['password'] = self.password
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.pixmapReady.disconnect(self.receivedImage)
        self.storeConfig()
        super().closeEvent(closeEvent)
