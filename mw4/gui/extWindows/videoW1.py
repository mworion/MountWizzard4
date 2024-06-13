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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PySide6.QtCore import Signal

# local import
from gui.extWindows.videoW import VideoWindow


class VideoWindow1(VideoWindow):
    """
    """
    __all__ = ['VideoWindow1']

    pixmapReady = Signal(object)

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
        if 'videoW1' not in config:
            config['videoW1'] = {}
        else:
            config['videoW1'].clear()
        config = config['videoW1']

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
