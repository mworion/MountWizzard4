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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from queue import Queue

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from mountcontrol.mount import Mount
from skyfield.toposlib import Topos

# local import
from mw4.gui.satelliteW import SatelliteWindow
from mw4.resource import resources


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global Test

    class Test1:
        horizonP = {(10, 0), (15, 360)}

    class Test(QObject):
        config = {'mainW': {}}
        update1s = pyqtSignal()
        messageQueue = Queue()
        threadPool = QThreadPool()
        mount = Mount()
        data = Test1()
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

    yield
    del Test


def test_initConfig_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.app.config['satelliteW'] = {}
    suc = app.initConfig()
    assert suc


def test_initConfig_2(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    del app.app.config['satelliteW']
    suc = app.initConfig()
    assert suc


def test_initConfig_3(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.app.config['satelliteW'] = {}
    app.app.config['satelliteW']['winPosX'] = 10000
    app.app.config['satelliteW']['winPosY'] = 10000
    suc = app.initConfig()
    assert suc


def test_storeConfig(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.storeConfig()


def test_resizeEvent(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.resizeEvent(None)


def test_receiveSatelliteAndShow_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.receiveSatelliteAndShow()
    assert not suc


def test_receiveSatelliteAndShow_2(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.receiveSatelliteAndShow(satellite=None)
    assert not suc


def test_updatePositions_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.updatePositions()
    assert not suc


def test_updatePositions_2(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.updatePositions(observe='t')
    assert not suc


def test_updatePositions_3(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.updatePositions(observe='t', subpoint='t')
    assert not suc

"""
def test_updatePositions_4(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.updatePositions(observe=observe,
                              subpoint=subpoint,
                              altaz=altaz)
    assert suc
"""