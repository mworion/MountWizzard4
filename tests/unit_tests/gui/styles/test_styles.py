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
import unittest.mock as mock
import pytest
import platform

# external packages

# local import
from gui.styles.styles import Styles


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    window = Styles()
    yield window


def test_property(function):
    a = function.M_TRANS
    a = function.M_PRIM
    a = function.M_PRIM1
    a = function.M_PRIM2
    a = function.M_PRIM3
    a = function.M_PRIM4
    a = function.M_TER
    a = function.M_TER1
    a = function.M_TER2
    a = function.M_SEC
    a = function.M_SEC1
    a = function.M_BACK
    a = function.M_BACK1
    a = function.M_GRAY
    a = function.M_RED
    a = function.M_RED1
    a = function.M_RED2
    a = function.M_YELLOW
    a = function.M_YELLOW1
    a = function.M_YELLOW2
    a = function.M_GREEN
    a = function.M_GREEN1
    a = function.M_GREEN2
    a = function.M_PINK
    a = function.M_PINK1
    a = function.M_CYAN
    a = function.M_CYAN1
    a = function.M_TAB
    a = function.M_TAB1
    a = function.M_TAB2


def test_mw4Style_1(function):
    with mock.patch.object(platform, "system", return_value="Darwin"):
        ret = function.mw4Style
        assert ret.startswith("\n")


def test_mw4Style_2(function):
    with mock.patch.object(platform, "system", return_value="Windows"):
        ret = function.mw4Style
        assert ret.startswith("\n")


def test_calcHexColor_1(function):
    val = function.calcHexColor("#808080", 1)
    assert val == "#808080"


def test_calcHexColor_2(function):
    val = function.calcHexColor("#80808000", 1)
    assert val == "#808080"


def test_calcHexColor_3(function):
    val = function.calcHexColor("#808080", 0.5)
    assert val == "#404040"


def test_findKeysInLine_1(function):
    inStyle = "12345$M_PRIM$12345#GRAD_1#%ROUND%;"
    function.colorSet = 0
    val = function.findKeysInLine(inStyle, "$")
    assert val[0] == "M_PRIM"


def test_findKeysInLine_2(function):
    inStyle = "12345$M_PRIM$12345#GRAD_1#%ROUND%;"
    function.colorSet = 0
    val = function.findKeysInLine(inStyle, "#")
    assert val[0] == "GRAD_1"


def test_findKeysInLine_3(function):
    inStyle = "12345 $M_PRIM$12345#GRAD_1#%ROUND%;"
    function.colorSet = 0
    val = function.findKeysInLine(inStyle, "%")
    assert val[0] == "ROUND"


def test_replaceColor_1(function):
    inStyle = "12345 $M_PRIM$;"
    function.colorSet = 0
    val = function.replaceColor(inStyle)
    assert val == "12345 #2090C0;"


def test_replaceForm_1(function):
    inStyle = "12345 %ROUND%;"
    function.colorSet = 0
    val = function.replaceForm(inStyle)
    assert val == "12345 2px;"


def test_insertGradient_1(function):
    inStyle = "12345 #GRAD_1,$M_PRIM$#;"
    function.colorSet = 0
    val = function.insertGradient(inStyle)
    assert val == "12345 $M_PRIM$;"


def test_insertGradient_2(function):
    inStyle = "12345 #GRAD_1,$M_PRIM$#;"
    function.colorSet = 1
    val = function.insertGradient(inStyle)
    assert (
        val
        == "12345 qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:0.15, stop:0 $M_TER$, stop:0.25 $M_TER2$, stop:1 $M_PRIM$);"
    )


def test_renderStyle_1(function):
    inStyle = "12345$M_PRIM$12345"
    function.colorSet = 0
    val = function.renderStyle(inStyle).strip(" ")
    assert val == "12345#2090C012345\n"


def test_renderStyle_2(function):
    inStyle = "12345$M_TEST$12345"
    function.colorSet = 0
    val = function.renderStyle(inStyle).strip(" ")
    assert val == "12345$M_TEST$12345\n"
