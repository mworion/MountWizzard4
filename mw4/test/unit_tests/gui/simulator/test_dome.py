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
from PyQt5.Qt3DExtras import Qt3DWindow
from PyQt5.QtCore import QObject
from mountcontrol.mount import Mount
from skyfield.api import Topos

# local import
from mw4.gui.simulator.dome import SimulatorDome


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

    app = SimulatorDome(app=Test())
    yield


def test_create_1():
    app.modelRoot = QEntity()
    suc = app.create(QEntity(), False)
    assert not suc


def test_create_2():
    app.modelRoot = QEntity()
    app.model = {'test': {'e': QEntity()}}
    suc = app.create(QEntity(), False)
    assert not suc


def test_create_3():
    app.modelRoot = QEntity()
    app.model = {'test': {'e': QEntity()}}
    suc = app.create(app.modelRoot, True)
    assert suc
