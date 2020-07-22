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
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.Qt3DCore import QEntity
from PyQt5.QtCore import QObject
from mountcontrol.mount import Mount
from skyfield.api import Topos

# local import
from mw4.gui.simulator.pointer import SimulatorPointer


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app

    class Test(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData='mw4/test/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        mwGlob = {'modelDir': 'mw4/test/model',
                  'imageDir': 'mw4/test/image'}
        uiWindows = {'showImageW': {'classObj': None}}

    app = SimulatorPointer(app=Test())
    yield


def test_create_1(qtbot):
    e = QEntity()
    suc = app.create(e, False)
    assert not suc


def test_create_2(qtbot):
    e = QEntity()
    app.modelRoot = e
    app.model = {'test': {'e': e}}
    suc = app.create(e, False)
    assert not suc


def test_create_3(qtbot):
    e = QEntity()
    app.modelRoot = e
    app.model = {'test': {'e': e}}
    suc = app.create(e, True)
    assert suc
