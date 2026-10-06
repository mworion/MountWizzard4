# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

from mw4.base.ethernet import checkFormatMAC


def test_checkFormatMAC_1():
    val = checkFormatMAC("")
    assert not val


def test_checkFormatMAC_2():
    val = checkFormatMAC(1234)
    assert not val


def test_checkFormatMAC_3():
    val = checkFormatMAC("00:00:00")
    assert not val


def test_checkFormatMAC_4():
    val = checkFormatMAC("00:00:00:123:00:00")
    assert not val


def test_checkFormatMAC_5():
    val = checkFormatMAC("00:00:00:12K:00:00")
    assert not val


def test_checkFormatMAC_6():
    val = checkFormatMAC("00:00:00:12:00:00")
    assert val == "00:00:00:12:00:00"


def test_checkFormatMAC_7():
    val = checkFormatMAC("00:L0:00:12:00:00")
    assert not val
