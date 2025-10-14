############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from mw4.base.driverDataClass import DriverData
from mw4.base.loggerMW import setupLogging

setupLogging()

app = DriverData()


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
