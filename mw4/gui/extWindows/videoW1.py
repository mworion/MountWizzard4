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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from gui.extWindows.videoW import VideoWindow


class VideoWindow1(VideoWindow):
    """ """

    def __init__(self, app):
        super().__init__(app=app)
        self.setWindowTitle("Video Stream 1")
        self.setObjectName("Video1")

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("videoW1", {})

        self.positionWindow(config)
        self.ui.videoURL.setText(config.get("videoURL", ""))
        self.ui.videoSource.setCurrentIndex(config.get("videoSource", 0))
        self.ui.frameRate.setCurrentIndex(config.get("frameRate", 2))
        self.user = config.get("user", "")
        self.password = config.get("password", "")

    def storeConfig(self) -> None:
        """ """
        configMain = self.app.config
        configMain["videoW1"] = {}
        config = configMain["videoW1"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()
        config["videoURL"] = self.ui.videoURL.text()
        config["videoSource"] = self.ui.videoSource.currentIndex()
        config["frameRate"] = self.ui.frameRate.currentIndex()
        config["user"] = self.user
        config["password"] = self.password

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.pixmapReady.disconnect(self.receivedImage)
        self.storeConfig()
        super().closeEvent(closeEvent)
