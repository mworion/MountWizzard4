# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.driverDataClass import DriverData

data = {}
app = DriverData(data)


def test_storeAscomProperty_1():
    app.data = {"YES": 0}

    app.storePropertyToData(None, "YES")
    assert "YES" not in app.data


def test_storeAscomProperty_2():
    app.data = {"NO": 0}

    app.storePropertyToData(None, "YES")
    assert "YES" in app.data


def test_storeAscomProperty_3():
    app.data = {"YES": 0, "NO": 0}

    app.storePropertyToData(10, "YES")
    assert "YES" in app.data
    assert "NO" in app.data


def test_storeAscomProperty_4():
    app.data = {}

    app.storePropertyToData(10, "YES")
    assert "YES" in app.data


def test_storeAscomProperty_5():
    app.data = {"NO": 0}

    app.storePropertyToData(None, "YES")
    assert "YES" in app.data
    assert "NO" in app.data
