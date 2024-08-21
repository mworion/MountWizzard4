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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import astropy
from unittest import mock

# external packages
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.simulatorW import SimulatorWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func,
                           'show'):
        yield func.telescope


def test_updatePositions_1(function):
    function.app.deviceStat['mount'] = False
    function.updatePositions()


def test_updatePositions_2(function):
    function.parent.entityModel['mountBase'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['mountBase']['trans'] = t
    function.parent.entityModel['mountBase']['entity'].addComponent(t)

    function.parent.entityModel['lat'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['lat']['trans'] = t
    function.parent.entityModel['lat']['entity'].addComponent(t)

    function.parent.entityModel['gem'] = {'entity': Qt3DCore.QEntity()}
    m = Qt3DExtras.QCuboidMesh()
    t = Qt3DCore.QTransform()
    function.parent.entityModel['gem']['mesh'] = m
    function.parent.entityModel['gem']['trans'] = t
    function.parent.entityModel['gem']['entity'].addComponent(m)
    function.parent.entityModel['gem']['entity'].addComponent(t)

    function.parent.entityModel['gemCorr'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['gemCorr']['trans'] = t
    function.parent.entityModel['gemCorr']['entity'].addComponent(t)

    function.parent.entityModel['otaRing'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['otaRing']['trans'] = t
    function.parent.entityModel['otaRing']['entity'].addComponent(t)

    function.parent.entityModel['otaTube'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['otaTube']['trans'] = t
    function.parent.entityModel['otaTube']['entity'].addComponent(t)

    function.parent.entityModel['otaImagetrain'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['otaImagetrain']['trans'] = t
    function.parent.entityModel['otaImagetrain']['entity'].addComponent(t)

    function.app.deviceStat['mount'] = True
    function.updatePositions()


def test_updateRotation_1(function):
    function.app.mount.obsSite.angularPosRA = None
    function.app.mount.obsSite.angularPosDEC = None
    function.updateRotation()


def test_updateRotation_2(function):
    function.app.mount.obsSite.angularPosRA = Angle(degrees=10)
    function.app.mount.obsSite.angularPosDEC = Angle(degrees=10)
    function.parent.entityModel['ra'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['ra']['entity'].addComponent(t)
    function.parent.entityModel['ra']['trans'] = t

    function.parent.entityModel['dec'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['dec']['entity'].addComponent(t)
    function.parent.entityModel['dec']['trans'] = t
    function.updateRotation()


def test_create_1(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=10)
    with mock.patch.object(function,
                           'updatePositions'):
        with mock.patch.object(function,
                               'updateRotation'):
            function.create()


def test_create_2(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=-10)
    with mock.patch.object(function,
                           'updatePositions'):
        with mock.patch.object(function,
                               'updateRotation'):
            function.create()

