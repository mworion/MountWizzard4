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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform
# external packages
import PyQt5.QtWidgets
import PyQt5.QtGui
# local imports
from baseclasses import styles

import time


class MWidget(PyQt5.QtWidgets.QWidget, styles.MWStyles):
    """
    MWidget defines the common parts for all windows used in MountWizzard 4. namely the
    sizes and the styles. styles are defined separately in a css looking stylesheet.
    standard screen size will be 800x600 pixel
    """

    logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()
        self.palette = PyQt5.QtGui.QPalette()
        self.initUI()
        self.screenSizeX = PyQt5.QtWidgets.QDesktopWidget().screenGeometry().width()
        self.screenSizeY = PyQt5.QtWidgets.QDesktopWidget().screenGeometry().height()
        self.showStatus = False

    def closeEvent(self, closeEvent):
        self.showStatus = False
        # if we close the main window, the application will be finished as well
        if self.windowTitle().startswith('MountWizzard'):
            self.quit()

    @staticmethod
    def widgetIcon(gui, icon):
        """
        widget icon adds an icon to a gui element like an button.

        :param      gui:        gui element, which will be expanded by an icon
        :param      icon:       icon to be added
        :return:    nothing
        """
        gui.setIcon(PyQt5.QtGui.QIcon(icon))
        gui.setProperty('iconset', True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)
        gui.setIconSize(PyQt5.QtCore.QSize(16, 16))

    def initUI(self):
        """
        init_UI makes the basic initialisation of the GUI. is sets the window flags
        and sets the handling of the window. is as well fixes the windows size (unless
        a windows will be scalable later on. in addition the appropriate style sheet
        for mac and non mac will be selected and used.

        :return:    nothing
        """

        self.setWindowFlags((self.windowFlags()
                             | PyQt5.QtCore.Qt.CustomizeWindowHint)
                            & ~PyQt5.QtCore.Qt.WindowMaximizeButtonHint)
        self.setMouseTracking(True)
        # sizing in gui should be fixed, because I have a static layout
        self.setFixedSize(800, 600)
        self.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))
        if platform.system() == 'Darwin':
            self.setStyleSheet(self.MAC_STYLE + self.BASIC_STYLE)
        else:
            self.setStyleSheet(self.NON_MAC_STYLE + self.BASIC_STYLE)

    @staticmethod
    def changeStylesheet(ui, item, value):
        """
        changeStylesheet changes the stylesheet of a given uii element and makes it
        visible. therefore the element has to be unpolished and polished again.

        :param      ui:     ui element, where the stylesheet has to be changed
        :param      item:   stylesheet attribute which has to be changes
        :param      value:  new value of the attribute
        :return:
        """

        ui.setProperty(item, value)
        ui.style().unpolish(ui)
        ui.style().polish(ui)
