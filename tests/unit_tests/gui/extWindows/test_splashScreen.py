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
from mw4.gui.extWindows.splashScreen import SplashScreen
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget
from unittest import mock


def test_init_1():
    mock_qapp = mock.MagicMock(spec=QApplication)
    mock_pixmap = mock.MagicMock()
    mock_splash = mock.MagicMock()

    with (
        mock.patch("mw4.gui.extWindows.splashScreen.QApplication.processEvents"),
        mock.patch("mw4.gui.extWindows.splashScreen.as_file") as mock_as_file,
        mock.patch("mw4.gui.extWindows.splashScreen.QPixmap", return_value=mock_pixmap),
        mock.patch("mw4.gui.extWindows.splashScreen.QSplashScreen", return_value=mock_splash),
    ):
        mock_as_file.return_value.__enter__.return_value = Path("test.png")
        splash = SplashScreen(mock_qapp)
        assert splash._qapp == mock_qapp
        assert splash._pxm == mock_pixmap
        assert splash.qss == mock_splash


def test_init_2():
    mock_pixmap = mock.MagicMock()
    mock_splash = mock.MagicMock()

    with (
        mock.patch("mw4.gui.extWindows.splashScreen.QApplication.processEvents"),
        mock.patch("mw4.gui.extWindows.splashScreen.as_file") as mock_as_file,
        mock.patch("mw4.gui.extWindows.splashScreen.QPixmap", return_value=mock_pixmap),
        mock.patch("mw4.gui.extWindows.splashScreen.QSplashScreen", return_value=mock_splash),
    ):
        mock_as_file.return_value.__enter__.return_value = Path("test.png")
        splash = SplashScreen(None)
        assert splash._qapp is None
        assert splash._pxm == mock_pixmap
        assert splash.qss == mock_splash


def test_close_1():
    mock_pixmap = mock.MagicMock()
    mock_splash = mock.MagicMock()

    with (
        mock.patch("mw4.gui.extWindows.splashScreen.QApplication.processEvents"),
        mock.patch("mw4.gui.extWindows.splashScreen.as_file") as mock_as_file,
        mock.patch("mw4.gui.extWindows.splashScreen.QPixmap", return_value=mock_pixmap),
        mock.patch("mw4.gui.extWindows.splashScreen.QSplashScreen", return_value=mock_splash),
    ):
        mock_as_file.return_value.__enter__.return_value = Path("test.png")
        splash = SplashScreen(None)
        splash.close()
        mock_splash.close.assert_called_once()


def test_finish_1():
    mock_pixmap = mock.MagicMock()
    mock_splash = mock.MagicMock()
    qwid = mock.MagicMock(spec=QWidget)

    with (
        mock.patch("mw4.gui.extWindows.splashScreen.QApplication.processEvents"),
        mock.patch("mw4.gui.extWindows.splashScreen.as_file") as mock_as_file,
        mock.patch("mw4.gui.extWindows.splashScreen.QPixmap", return_value=mock_pixmap),
        mock.patch("mw4.gui.extWindows.splashScreen.QSplashScreen", return_value=mock_splash),
    ):
        mock_as_file.return_value.__enter__.return_value = Path("test.png")
        splash = SplashScreen(None)
        splash.finish(qwid)
        mock_splash.finish.assert_called_once_with(qwid)
