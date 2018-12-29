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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import PyQt5
# external packages
import skyfield.api
# local import
from mw4 import mainApp

from mw4.modeldata import hipparcos

test = PyQt5.QtWidgets.QApplication([])
mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'dataDir': './mw4/test/config',
          'modeldata': 'test',
          }
app = mainApp.MountWizzard4(mwGlob=mwGlob)
topo = skyfield.toposlib.Topos(longitude_degrees=11,
                               latitude_degrees=48,
                               elevation_m=500)
app.mount.obsSite.location = topo
data = hipparcos.Hipparcos(app=app,
                           mwGlob=mwGlob)
