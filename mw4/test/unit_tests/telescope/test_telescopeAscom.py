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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import platform
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
if platform.system() == 'Windows':
    import win32com.client
    import pythoncom

# local import
from mw4.telescope.telescopeAscom import TelescopeAscom
from mw4.telescope.telescope import TelescopeSignals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        ApertureDiameter = 100
        FocalLength = 570
        connected = True
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = TelescopeAscom(app=Test(), signals=TelescopeSignals(), data={})
    app.client = Test1()
    yield


def test_getInitialConfig_1():
    suc = app.getInitialConfig()
    assert suc


def test_getInitialConfig_2():
    suc = app.getInitialConfig()
    assert suc
    assert app.data['TELESCOPE_INFO.TELESCOPE_APERTURE'] == 100
    assert app.data['TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH'] == 570

