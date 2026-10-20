# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import hashlib
import json
import pytest
import re
from importlib.resources import files
from mw4.gui.styles.colors import colors
from mw4.gui.styles.images import images
from mw4.gui.styles.styles import Styles, loadTemplate
from pathlib import Path
from tests.unit_tests.unitTestAddOns.platformStub import patchPlatform


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


def test_mw4Style_1(function):
    with patchPlatform("Darwin"):
        ret = function.mw4Style
        assert ret.startswith("\n")


def test_mw4Style_2(function):
    with patchPlatform("Windows"):
        ret = function.mw4Style
        assert ret.startswith("\n")


def test_mw4Style_nonDarwin_nocache(function):
    function.cachedStyle = None
    function.cachedColorSet = None
    with patchPlatform("Linux"):
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


def test_hex2rgb_without_alpha(function):
    result = function.hex2rgb("#2090C0")
    assert result == [32, 144, 192]


def test_hex2rgb_with_alpha(function):
    result = function.hex2rgb("#2090C0FF")
    assert result == [32, 144, 192, 255]


def test_rgb2hex_without_alpha(function):
    result = function.rgb2hex([32, 144, 192])
    assert result == "#2090c0"


def test_rgb2hex_with_alpha(function):
    result = function.rgb2hex([32, 144, 192, 255])
    assert result == "#2090c0ff"


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


@pytest.mark.parametrize("name", ["mac", "nonMac", "basic"])
def test_loadTemplate(name):
    template = loadTemplate(name)
    assert isinstance(template, str)
    assert template.strip()


def test_styleTemplate_pickedPerPlatform(function):
    with patchPlatform("Darwin"):
        mac = function.styleTemplate()
    with patchPlatform("Linux"):
        nonMac = function.styleTemplate()
    with patchPlatform("Windows"):
        windows = function.styleTemplate()
    assert mac == loadTemplate("mac") + loadTemplate("basic")
    assert nonMac == loadTemplate("nonMac") + loadTemplate("basic")
    assert windows == nonMac


@pytest.mark.parametrize("name", ["mac", "nonMac", "basic"])
def test_templateKeysAreKnown(name):
    for key in re.findall(r"\$([\w-]+)\$", loadTemplate(name)):
        assert key in colors or key in images, key


def test_renderedStyleMatchesGolden(function):
    golden = json.loads(Path("tests/testData/styleGolden.json").read_text())
    iconDir = str(files("mw4").joinpath("assets/icon"))
    for key, digest in golden.items():
        platformName, colorSet, transparency = key.split("-")
        system = "Darwin" if platformName == "mac" else "Linux"
        function.colorSet = int(colorSet)
        function.transparency = float(transparency)
        with patchPlatform(system):
            rendered = function.renderStyle(function.styleTemplate())
        rendered = rendered.replace(iconDir, "<ICON>")
        assert hashlib.sha256(rendered.encode()).hexdigest() == digest, key
    function.colorSet = 0
    function.transparency = 1.0
