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
    assert isinstance(function.M_PRIM, list)
    assert isinstance(function.M_PRIM1, list)
    assert isinstance(function.M_PRIM2, list)
    assert isinstance(function.M_PRIM3, list)
    assert isinstance(function.M_PRIM4, list)
    assert isinstance(function.M_SEC, list)
    assert isinstance(function.M_SEC1, list)
    assert isinstance(function.M_TER, list)
    assert isinstance(function.M_TER1, list)
    assert isinstance(function.M_TER2, list)
    assert isinstance(function.M_BACK, list)
    assert isinstance(function.M_BACK1, list)
    assert isinstance(function.M_GRAY, list)
    assert isinstance(function.M_RED, list)
    assert isinstance(function.M_RED1, list)
    assert isinstance(function.M_RED2, list)
    assert isinstance(function.M_YELLOW, list)
    assert isinstance(function.M_YELLOW1, list)
    assert isinstance(function.M_YELLOW2, list)
    assert isinstance(function.M_GREEN, list)
    assert isinstance(function.M_GREEN1, list)
    assert isinstance(function.M_GREEN2, list)
    assert isinstance(function.M_PINK, list)
    assert isinstance(function.M_PINK1, list)
    assert isinstance(function.M_CYAN, list)
    assert isinstance(function.M_CYAN1, list)
    assert isinstance(function.M_TAB, list)
    assert isinstance(function.M_TAB1, list)
    assert isinstance(function.M_TAB2, list)


def test_mw4Style_1(function):
    with mock.patch.object(platform, "system", return_value="Darwin"):
        ret = function.mw4Style
        assert ret.startswith("\n")


def test_mw4Style_2(function):
    with mock.patch.object(platform, "system", return_value="Windows"):
        ret = function.mw4Style
        assert ret.startswith("\n")


def test_mw4Style_nonDarwin_nocache(function):
    function.cachedStyle = None
    function.cachedColorSet = None
    with mock.patch.object(platform, "system", return_value="Linux"):
        ret = function.mw4Style
        assert ret.startswith("\n")


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
    assert val == "12345 rgba(32, 144, 192, 255);"


def test_replaceImage_1(function):
    inStyle = "12345 $checkmark$;"
    function.colorSet = 0
    val = function.replaceImage(inStyle)
    assert val.startswith("12345 ")
    assert val.endswith(".svg;")


def test_renderStyle_1(function):
    inStyle = "12345$M_PRIM$12345"
    function.colorSet = 0
    val = function.renderStyle(inStyle).strip(" ")
    assert val == "12345rgba(32, 144, 192, 255)12345\n"


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
