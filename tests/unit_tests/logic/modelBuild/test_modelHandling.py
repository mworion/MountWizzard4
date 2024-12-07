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

# external packages
from skyfield.api import wgs84

# local import
from mountcontrol.model import Model, ModelStar
from mountcontrol import obsSite
from logic.modelBuild.modelHandling import writeRetrofitData

obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)


def test_writeRetrofitData_1():
    class Parent:
        host = None

    mountModel = Model(parent=Parent())

    val = writeRetrofitData(mountModel, [])
    assert val == []


def test_writeRetrofitData_2():
    class Parent:
        host = None

    mountModel = Model(parent=Parent())
    p1 = "12:45:33.01"
    p2 = "+56*30:00.5"
    p3 = "1234.5"
    p4 = "90"
    p5 = obsSite
    modelStar1 = ModelStar(
        coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=1, obsSite=p5
    )

    mountModel.addStar(modelStar1)
    buildModel = [{"test": 1}]

    val = writeRetrofitData(mountModel, buildModel)
    assert "errorRMS" in val[0]
    assert "modelPolarError" in val[0]
