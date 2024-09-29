#############################################################
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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import time
from pathlib import Path

# external packages
from PySide6.QtCore import Signal, QObject
from skyfield.api import Angle

# local imports
from base.transform import JNowToJ2000, J2000ToJNow
from gui.utilities.toolsQtWidget import sleepAndEvents


