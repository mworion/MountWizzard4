############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from mw4.gui.extWindows.video.videoBase import VideoWindowBase
from typing import Any


class VideoWindow(VideoWindowBase):
    def __init__(self, app: Any, title: str) -> None:
        super().__init__(app=app)
        self.title: str = "Window" + title
        self.setWindowTitle(title)

    def initConfig(self) -> None:
        config = self.app.config.get(self.title, {})

        self.setPositionWindow(config)
        self.ui.videoURL.setText(config.get("videoURL", ""))
        self.ui.videoSource.setCurrentIndex(config.get("videoSource", 0))
        self.ui.frameRate.setCurrentIndex(config.get("frameRate", 2))
        self.user = config.get("user", "")
        self.password = config.get("password", "")

    def storeConfig(self) -> None:
        configMain = self.app.config
        configMain[self.title] = {}
        config = configMain[self.title]

        self.getPositionWindow(config)
        config["videoURL"] = self.ui.videoURL.text()
        config["videoSource"] = self.ui.videoSource.currentIndex()
        config["frameRate"] = self.ui.frameRate.currentIndex()
        config["user"] = self.user
        config["password"] = self.password

    def closeEvent(self, closeEvent) -> None:
        self.pixmapReady.disconnect(self.receivedImage)
        self.storeConfig()
        super().closeEvent(closeEvent)
