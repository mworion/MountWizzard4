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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from PyQt5.Qt3DCore import QEntity

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.simulator.horizon import SimulatorHorizon


@pytest.fixture(autouse=True, scope='function')
def function():
    func = SimulatorHorizon(app=App())
    yield func


def test_createWall_1(function):
    val = function.createWall(QEntity(), 0, 0, 10)
    assert isinstance(val, QEntity)


def test_create_1(function):
    e = QEntity()
    suc = function.create(e, False)
    assert not suc


def test_create_2(function):
    e = QEntity()
    function.modelRoot = e
    function.model = {'test': {'e': e}}
    suc = function.create(e, False)
    assert not suc


def test_create_3(function):
    e = QEntity()
    function.app.data.horizonP = None
    function.modelRoot = e
    function.model = {'test': {'e': e}}
    suc = function.create(e, True)
    assert not suc


def test_create_4(function):
    function.horizon = [
        {'e': QEntity()},
    ]
    function.app.data.horizonP = [(0, 0), (10, 10)]
    function.horizonRoot = QEntity()
    e = QEntity()
    function.modelRoot = e
    function.model = {'test': {'e': e}}
    suc = function.create(e, True)
    assert suc
