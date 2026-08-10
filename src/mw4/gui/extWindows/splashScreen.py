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
from importlib.resources import as_file, files
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen, QWidget


class SplashScreen:
    def __init__(self, application: QApplication | None = None) -> None:
        self._qapp = application
        with as_file(files("mw4").joinpath("assets/icon/mw4.png")) as imageFile:
            self._pxm = QPixmap(str(imageFile))
        flags = Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.X11BypassWindowManagerHint
        self.qss = QSplashScreen(self._pxm, flags)
        self.qss.show()
        self.qss.raise_()
        QApplication.processEvents()

    def close(self) -> None:
        self.qss.close()

    def finish(self, qwid: QWidget) -> None:
        self.qss.finish(qwid)
