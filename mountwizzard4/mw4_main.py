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
import os
# external packages
import PyQt5.QtCore
# local import
from mountcontrol.mount import Mount
from mountwizzard4.gui.mainW import MainWindow


class MountWizzard4(object):
    """
    MountWizzard4 class is the main class for the application. it loads all windows and
    classes needed to fulfil the work of mountwizzard. any gui work should be handled
    through the window classes. main class is for setup, config, start, persist and
    shutdown the application.
    """

    __all__ = ['MountWizzard4',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

        # get the working horses up
        self.mount = Mount('192.168.2.15', pathToTS=os.getcwd() + '/config')
        # get the window widgets up
        self.mainW = MainWindow(self)
        self.mainW.show()

        self.mount.signals.pointDone.connect(self.mainW.updatePointGUI)
        self.mount.signals.setDone.connect(self.mainW.updateSetGUI)
        self.mount.startTimers()

    def quit(self):
        self.mount.stopTimers()
        PyQt5.QtCore.QCoreApplication.quit()
