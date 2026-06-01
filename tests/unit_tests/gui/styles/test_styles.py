############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

import platform
import pytest
import unittest.mock as mock
from mw4.gui.styles.styles import Styles


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    window = Styles()
    yield window


def test_property(function):
    a = ""
    a += function.M_TRANS
    a += function.M_PRIM
    a += function.M_PRIM1
    a += function.M_PRIM2
    a += function.M_PRIM3
    a += function.M_PRIM4
    a += function.M_SEC
    a += function.M_SEC1
    a += function.M_TER
    a += function.M_TER1
    a += function.M_TER2
    a += function.M_BACK
    a += function.M_BACK1
    a += function.M_GRAY
    a += function.M_RED
    a += function.M_RED1
    a += function.M_RED2
    a += function.M_YELLOW
    a += function.M_YELLOW1
    a += function.M_YELLOW2
    a += function.M_GREEN
    a += function.M_GREEN1
    a += function.M_GREEN2
    a += function.M_PINK
    a += function.M_PINK1
    a += function.M_CYAN
    a += function.M_CYAN1
    a += function.M_TAB
    a += function.M_TAB1
    a += function.M_TAB2
    assert a != 0


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


def test_replaceImage_1(function):
    inStyle = "12345 $checkmark$;"
    function.colorSet = 0
    val = function.replaceImage(inStyle)
    assert val.startswith("12345 ")
    assert val.endswith(".svg;")


def test_insertGradient_1(function):
    inStyle = "12345 #GRAD_1,$M_PRIM$#;"
    function.colorSet = 0
    val = function.insertGradient(inStyle)
    assert val == "12345 $M_PRIM$;"


def test_insertGradient_2(function):
    inStyle = "12345 #GRAD_1,$M_PRIM$#;"
    function.colorSet = 1
    val = function.insertGradient(inStyle)
    expected = (
        "12345 qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:0.15,"
        " stop:0 $M_TER$, stop:0.25 $M_TER2$, stop:1 $M_PRIM$);"
    )
    assert val == expected


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


def test_mw4Style_caching_same_colorSet(function):
    """Test that mw4Style returns cached value when colorSet doesn't change"""
    function.colorSet = 0
    function.cachedStyle = None
    function.cachedColorSet = None

    # First call should compute and cache
    style1 = function.mw4Style
    cachedStyle = function.cachedStyle
    cachedColorSet = function.cachedColorSet

    # Second call should return cached value
    style2 = function.mw4Style

    assert style1 == style2
    assert cachedStyle == function.cachedStyle
    assert cachedColorSet == function.cachedColorSet
    assert cachedColorSet == 0


def test_mw4Style_caching_different_colorSet(function):
    """Test that mw4Style recomputes when colorSet changes"""
    function.colorSet = 0
    function.cachedStyle = None
    function.cachedColorSet = None

    # Get style for colorSet 0
    style1 = function.mw4Style
    cachedStyle1 = function.cachedStyle

    # Change colorSet
    function.colorSet = 1

    # Get style for colorSet 1 - should recompute
    style2 = function.mw4Style
    cachedStyle2 = function.cachedStyle

    # Styles should be different
    assert style1 != style2
    assert cachedStyle1 != cachedStyle2
    assert function.cachedColorSet == 1


def test_mw4Style_cache_invalidation(function):
    """Test that cache is properly invalidated on colorSet change"""
    function.colorSet = 0
    function.cachedStyle = None
    function.cachedColorSet = None

    # First call with colorSet 0
    style0_first = function.mw4Style

    # Change to colorSet 1
    function.colorSet = 1
    style1 = function.mw4Style

    # Change back to colorSet 0
    function.colorSet = 0
    style0_second = function.mw4Style

    # Style for colorSet 0 should be the same both times
    assert style0_first == style0_second
    # But different from colorSet 1
    assert style0_first != style1


