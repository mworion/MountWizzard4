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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PySide6.QtWidgets import QWidget
import numpy as np

# local import
from gui.utilities.gImageBar import ImageBar


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


def test_ImageBar_constructPlot():
    function = ImageBar()
    function.constructPlot()


def test_ImageBar_setColorMap():
    function = ImageBar()
    suc = function.setColorMap('plasma')
    assert suc


def test_ImageBar_setImage_1():
    function = ImageBar()
    suc = function.setImage(None)
    assert not suc


def test_ImageBar_setImage_2():
    function = ImageBar()
    img = np.random.rand(100, 100)
    suc = function.setImage(img)
    assert suc


def test_ImageBar_setImage_3():
    function = ImageBar()
    img = np.random.rand(100, 100)
    suc = function.setImage(img, False)
    assert suc


def test_ImageBar_showCrosshair():
    function = ImageBar()
    function.lx = QWidget()
    function.ly = QWidget()
    suc = function.showCrosshair(True)
    assert suc


def test_ImageBar_addEllipse():
    function = ImageBar()
    with mock.patch.object(function.p[0],
                           'addItem'):
        suc = function.addEllipse(0, 0, 1, 1, 0)
        assert suc


def test_ImageBar_addValueAnnotation():
    function = ImageBar()
    with mock.patch.object(function.p[0],
                           'addItem'):
        suc = function.addValueAnnotation(0, 0, 10)
        assert suc
