# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import platform
import pytest
import re
from mw4.base import platformInfo
from pathlib import Path
from tests.unit_tests.unitTestAddOns.platformStub import patchPlatform


def test_constantsMatchHost():
    assert platform.uname().system == platformInfo.SYSTEM
    assert (platformInfo.SYSTEM == "Windows") == platformInfo.IS_WINDOWS
    assert (platformInfo.SYSTEM == "Darwin") == platformInfo.IS_MAC
    assert (platformInfo.SYSTEM == "Linux") == platformInfo.IS_LINUX
    assert (".exe" if platformInfo.IS_WINDOWS else "") == platformInfo.EXE_SUFFIX


@pytest.mark.parametrize(
    "system, flags, suffix",
    [
        ("Windows", (True, False, False), ".exe"),
        ("Darwin", (False, True, False), ""),
        ("Linux", (False, False, True), ""),
        ("test", (False, False, False), ""),
    ],
)
def test_patchPlatform(system, flags, suffix):
    with patchPlatform(system):
        assert system == platformInfo.SYSTEM
        assert flags == (platformInfo.IS_WINDOWS, platformInfo.IS_MAC, platformInfo.IS_LINUX)
        assert suffix == platformInfo.EXE_SUFFIX


def test_registerWindowsBackends_onWindows():
    run = {"indi": 1}
    with patchPlatform("Windows"):
        platformInfo.registerWindowsBackends(run, {"ascom": lambda: 2, "sgpro": lambda: 3})
    assert run == {"indi": 1, "ascom": 2, "sgpro": 3}


@pytest.mark.parametrize("system", ["Darwin", "Linux"])
def test_registerWindowsBackends_offWindows(system):
    run = {"indi": 1}

    def factory() -> int:
        raise AssertionError("must not be called off Windows")

    with patchPlatform(system):
        platformInfo.registerWindowsBackends(run, {"ascom": factory})
    assert run == {"indi": 1}


def test_onlyPlatformInfoAsksTheSystem():
    offenders = [
        str(path)
        for path in Path("src/mw4").rglob("*.py")
        if path.name != "platformInfo.py" and re.search(r"platform\.system\(", path.read_text())
    ]
    assert not offenders
