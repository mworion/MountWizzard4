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
import math
import mw4.mountcontrol
import numpy
import skyfield.api
import unittest.mock as mock
from mw4.mountcontrol import obsSite
from mw4.mountcontrol.model import Model, ModelStar, ProgStar
from skyfield.api import Angle, Star, wgs84
from tests.unit_tests.unitTestAddOns.baseTestApp import App

obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)


class ObsSite:
    location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)


class Parent:
    obsSite = ObsSite()


#
#
# testing the class Model and it's attribute
#
#


def test_Model_altitudeError():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.altitudeError = Angle(degrees=67)
    assert align.altitudeError.degrees == 67


def test_Model_azimuthError():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.azimuthError = Angle(degrees=67)
    assert align.azimuthError.degrees == 67


def test_Model_polarError():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.polarError = Angle(degrees=67)
    assert align.polarError.degrees == 67


def test_Model_positionAngle1():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.positionAngle = Angle(degrees=67)
    assert align.positionAngle.degrees == 67


def test_Model_positionAngle2():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.positionAngle = Angle(degrees=67)
    assert align.positionAngle != 67


def test_Model_orthoError():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.orthoError = Angle(degrees=67)
    assert align.orthoError.degrees == 67


def test_Model_altitudeTurns():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.altitudeTurns = 67
    assert align.altitudeTurns == 67


def test_Model_azimuthTurns():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.azimuthTurns = 67
    assert align.azimuthTurns == 67


def test_Model_terms():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.terms = 67
    assert align.terms == 67


def test_Model_errorRMS():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.errorRMS = 67
    assert align.errorRMS == 67


def test_Model_numberStars_1():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.numberStars = "67"
    assert align.numberStars == 67
    assert align._numberStars == 67


def test_Model_numberStars_2():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.numberStars = None
    assert align.numberStars == 0
    assert align._numberStars == 0


def test_Model_numberNames_1():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.numberNames = "67"
    assert align.numberNames == 67
    assert align._numberNames == 67


def test_Model_numberNames_2():
    class Parent:
        host = None
        loggingTrace = False

    align = Model(parent=Parent())
    align.numberNames = None
    assert align.numberNames == 0
    assert align._numberNames == 0


def test_Model_starList1():
    p3 = 1234.5
    p4 = Angle(degrees=90)
    s = Star(ra_hours=12.7580583333, dec_degrees=56.5001388889)
    modelStar1 = ModelStar(s, p3, p4, number=1)

    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    assert len(model.starList) == 0
    model.starList = [modelStar1]
    assert len(model.starList) == 1


def test_add_del_Star():
    p1 = "12:45:33.01"
    p2 = "+56*30:00.5"
    p3 = "1234.5"
    p4 = "90"
    modelStar1 = ModelStar(coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=1)
    modelStar2 = ModelStar(coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=2)
    modelStar3 = ModelStar(coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=3)
    modelStar4 = ModelStar(coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=4)

    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    assert len(model.starList) == 0
    model.addStar(modelStar1)
    assert len(model.starList) == 1
    model.addStar(modelStar2)
    assert len(model.starList) == 2
    model.addStar(modelStar3)
    assert len(model.starList) == 3
    model.addStar(modelStar4)
    assert len(model.starList) == 4
    model.delStar(3)
    assert len(model.starList) == 3
    model.delStar(3)
    assert len(model.starList) == 3
    model.delStar(-1)
    assert len(model.starList) == 3
    model.delStar(1)
    assert len(model.starList) == 2


def test_addStar_ok():
    class Parent:
        host = None
        loggingTrace = False
        obsSite = None

    model = Model(parent=Parent())
    assert len(model.starList) == 0
    model.addStar("12:45:33.01,+56*30:00.5,1234.5,90,1")
    assert len(model.starList) == 1


def test_StarList_iteration():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    p4 = Angle(degrees=90)
    s = Star(ra_hours=12.7580583333, dec_degrees=56.5001388889)

    for i in range(0, 10):
        model.addStar(ModelStar(s, i * i, p4, i))

    assert len(model.starList) == 10
    for i, star in enumerate(model.starList):
        assert star.number == i
        assert star.errorRMS == i * i


def test_StarList_checkStarListOK():
    class Parent:
        host = None
        loggingTrace = False
        obsSite = None

    model = Model(parent=Parent())
    assert len(model.starList) == 0
    model.addStar("12:45:33.01,+56*30:00.5,1234.5,90,1")
    model.numberStars = 1
    assert model.checkStarListOK()


def test_StarList_checkStarList_not_OK1():
    class Parent:
        host = None
        loggingTrace = False
        obsSite = None

    model = Model(parent=Parent())
    assert len(model.starList) == 0
    model.addStar("12:45:33.01,+56*30:00.5,1234.5,90,1")
    model.numberStars = 2
    assert not model.checkStarListOK()

    class Parent:
        host = None
        loggingTrace = False
        obsSite = None

    model = Model(parent=Parent())
    assert len(model.starList) == 0
    model.addStar("12:45:33.01,+56*30:00.5,1234.5,90,1")
    assert not model.checkStarListOK()


def test_Model_nameList1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    assert len(model.nameList) == 0
    model.nameList = 67
    assert len(model.nameList) == 0


def test_Model_nameList2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    assert len(model.nameList) == 0
    model.nameList = ["67"]
    assert len(model.nameList) == 1


def test_Model_nameList3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    assert len(model.nameList) == 0
    model.nameList = ["67", "78"]
    assert len(model.nameList) == 2


def test_Model_nameList4():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    assert len(model.nameList) == 0
    model.nameList = ["67", 67]
    assert len(model.nameList) == 0


def test_add_del_Name():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    assert len(model.nameList) == 0
    model.addName("the first one")
    assert len(model.nameList) == 1
    model.addName("the second one")
    assert len(model.nameList) == 2
    model.addName("the third one")
    assert len(model.nameList) == 3
    model.addName("the fourth one")
    assert len(model.nameList) == 4


def test_addName_not_ok():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    assert len(model.nameList) == 0
    model.addName(45)
    assert len(model.nameList) == 0


#
#
# testing the specific QCI behavior in Model class attributes
#
#


def test_errorRMS_HPS():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.errorRMS = 36.8
    assert model.errorRMS == 36.8


def test_errorRMS_HPS_float():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.errorRMS = 36.8
    assert model.errorRMS == 36.8


def test_errorRMS_HPS_int():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.errorRMS = 36
    assert model.errorRMS == 36.0


#
#
# testing the class AlignStar and it's attribute setters
#
#


def test_AlignStar_coord1():
    p3 = 1234.5
    p4 = Angle(degrees=90)
    s = Star(ra_hours=12.7580583333, dec_degrees=56.5001388889)
    alignStar = ModelStar(s, p3, p4, number=1)
    assert math.isclose(alignStar.coord.ra.hms()[0], 12, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.ra.hms()[1], 45, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.ra.hms()[2], 29.01, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.dec.dms()[0], 56, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.dec.dms()[1], 30, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.dec.dms()[2], 0.5, abs_tol=1e-6)


def test_AlignStar_coord2():
    star = skyfield.api.Star(ra_hours=12.55, dec_degrees=56.55)
    p3 = 1234.5
    p4 = Angle(degrees=90)
    alignStar = ModelStar(coord=star, errorRMS=p3, errorAngle=p4, number=1)
    assert math.isclose(alignStar.coord.ra.hms()[0], 12, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.ra.hms()[1], 33, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.ra.hms()[2], 0, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.dec.dms()[0], 56, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.dec.dms()[1], 33, abs_tol=1e-6)
    assert math.isclose(alignStar.coord.dec.dms()[2], 0, abs_tol=1e-6)


def test_AlignStar_number():
    obsSite = App().mount.obsSite
    obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
    alignStar = ModelStar()
    alignStar.number = 6
    assert alignStar.number == 6


def test_AlignStar_errorAngle():
    obsSite = App().mount.obsSite
    obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
    alignStar = ModelStar()
    alignStar.errorAngle = Angle(degrees=50)
    assert alignStar.errorAngle.degrees == 50


def test_AlignStar_errorRMS():
    obsSite = App().mount.obsSite
    obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
    alignStar = ModelStar()
    alignStar.errorRMS = 6
    assert alignStar.errorRMS == 6


def test_AlignStar_error_DEC_RA():
    obsSite = App().mount.obsSite
    obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
    alignStar = ModelStar()
    alignStar.errorRMS = 6
    alignStar.errorAngle = Angle(degrees=50)
    ra = 6 * numpy.sin(50 * numpy.pi * 2 / 360)
    dec = 6 * numpy.cos(50 * numpy.pi * 2 / 360)
    assert math.isclose(alignStar.errorRA().degrees, ra, abs_tol=1e-7)
    assert math.isclose(alignStar.errorDEC().degrees, dec, abs_tol=1e-7)


def test_Model_parseNumberName_ok():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["5"]
    suc = model.parseNumberNames(response, 1)
    assert suc


def test_Model_parseNumberName_not_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["df"]
    suc = model.parseNumberNames(response, 1)
    assert suc


def test_Model_parseNumberName_not_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = [""]
    suc = model.parseNumberNames(response, 1)
    assert suc


def test_Model_parseNumberName_not_ok3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["5a"]
    suc = model.parseNumberNames(response, 1)
    assert suc


def test_Model_parseNumberName_not_ok4():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["5", "4"]
    suc = model.parseNumberNames(response, 1)
    assert not suc


def test_Model_parseNumberName_not_ok5():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["5", "g"]
    suc = model.parseNumberNames(response, 1)
    assert not suc


#
#
# testing modelNames
#
#


def test_Model_parseNames_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["test"]
    suc = model.parseNames(response, 1)
    assert suc


def test_Model_parseNames_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["sd", "", None]
    suc = model.parseNames(response, 3)
    assert suc


def test_Model_parseNumberNames_ok3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["5"]
    suc = model.parseNumberNames(response, 1)
    assert suc


def test_Model_parseNames_not_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["sd"]
    suc = model.parseNames(response, 3)
    assert not suc


def test_Model_parseNumberNames_not_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["sd"]
    suc = model.parseNumberNames(response, 1)
    assert suc


def test_Model_parseNumberNames_not_ok3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["5", "6"]
    suc = model.parseNumberNames(response, 2)
    assert not suc


def test_getNameCount_1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with mock.patch.object(
        mw4.mountcontrol.model.Connection,
        "communicate",
        return_value=(False, ["100"], 1),
    ):
        suc = model.getNameCount()
        assert not suc


def test_getNameCount_2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with mock.patch.object(
        mw4.mountcontrol.model.Connection,
        "communicate",
        return_value=(True, ["100"], 1),
    ):
        suc = model.getNameCount()
        assert suc


def test_getNames_1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.numberNames = 1
    with mock.patch.object(
        mw4.mountcontrol.model.Connection,
        "communicate",
        return_value=(False, ["100"], 1),
    ):
        suc = model.getNames()
        assert not suc


def test_getNames_2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.numberNames = 1
    with mock.patch.object(
        mw4.mountcontrol.model.Connection,
        "communicate",
        return_value=(True, ["100"], 1),
    ):
        suc = model.getNames()
        assert suc


def test_pollNames_1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with mock.patch.object(model, "getNameCount", return_value=False):
        suc = model.pollNames()
        assert not suc


def test_pollNames_2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with mock.patch.object(model, "getNameCount", return_value=True):
        with mock.patch.object(model, "getNames", return_value=False):
            suc = model.pollNames()
        assert not suc


def test_pollNames_3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with mock.patch.object(model, "getNameCount", return_value=True):
        with mock.patch.object(model, "getNames", return_value=True):
            suc = model.pollNames()
        assert suc


#
#
# testing model stars
#
#


def test_Model_parseNumberStars_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["0", "E"]
    suc = model.parseNumberStars(response, 2)
    assert suc


def test_Model_parseNumberStars_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = [
        "1",
        "023.8311, +24.8157, 29.8580, 227.45, -12.9985, +26.98, -08.97, 11, 97751.6",
    ]
    suc = model.parseNumberStars(response, 2)
    assert suc
    assert model.azimuthError.degrees == 23.8311
    assert model.altitudeError.degrees == 24.8157
    assert model.polarError.degrees == 29.8580
    assert model.positionAngle.degrees == 227.45
    assert model.orthoError.degrees == -12.9985
    assert model.azimuthTurns == 26.98
    assert model.altitudeTurns == -08.97
    assert model.errorRMS == 97751.6
    assert model.terms == 11


def test_Model_parseNumberStars_not_ok0():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["4", "E"]
    suc = model.parseNumberStars(response, 1)
    assert not suc


def test_Model_parseNumberStars_not_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["4"]
    suc = model.parseNumberStars(response, 1)
    assert not suc


def test_Model_parseNumberStars_not_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["4", "4, 4, 4"]
    suc = model.parseNumberStars(response, 2)
    assert not suc


def test_Model_parseNumberStars_not_ok3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    response = ["4", "4"]
    suc = model.parseNumberStars(response, 2)
    assert not suc


def test_Model_parseStars_ok():
    obsSite = App().mount.obsSite
    obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)

    class Parent:
        host = None
        loggingTrace = False
        obsSite = obsSite

    model = Model(parent=Parent())
    response = [
        "21:52:58.95,+08*56:10.1,   5.7,201",
        "21:06:10.79,+45*20:52.8,  12.1,329",
        "23:13:58.02,+38*48:18.8,  31.0,162",
        "17:43:41.26,+59*15:30.7,   8.4,005",
        "20:36:01.52,+62*39:32.4,  19.5,138",
        "03:43:11.04,+19*06:30.3,  22.6,199",
        "05:03:10.81,+38*14:22.2,  20.1,340",
        "04:12:55.39,+49*14:00.2,  17.1,119",
        "06:57:55.11,+61*40:26.8,   9.8,038",
        "22:32:24.00,+28*00:23.6,  42.1,347",
        "13:09:03.49,+66*24:40.5,  13.9,177",
    ]
    suc = model.parseStars(response, 11)
    assert suc
    assert len(model.starList) == 11


def test_Model_parseStars_not_ok1():
    obsSite = App().mount.obsSite
    obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)

    class Parent:
        host = None
        loggingTrace = False
        obsSite = obsSite

    model = Model(parent=Parent())
    response = [
        "21:52:58.95,+08*56:10.1,   5.7,201",
        "21:06:10.79,+45*20:52.8,  12.1,329",
        "23:13:58.02,+38*48:18.8,  31.0,162",
        "06:57:55.11,+61*40:26.8,   9.8,038",
        "22:32:24.00,+28*00:23.6,  42.1,347",
        "13:09:03.49,+66*24:40.5,  13.9,177",
    ]
    suc = model.parseStars(response, 4)
    assert not suc
    assert len(model.starList) == 0


def test_getStarCount_1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with (
        mock.patch.object(
            mw4.mountcontrol.model.Connection, "communicate", return_value=(False, ["100"], 1)
        ),
        mock.patch.object(model, "parseNumberStars", return_value=False),
    ):
        suc = model.getStarCount()
        assert not suc


def test_getStarCount_2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with (
        mock.patch.object(
            mw4.mountcontrol.model.Connection, "communicate", return_value=(True, ["100"], 1)
        ),
        mock.patch.object(model, "parseNumberStars", return_value=False),
    ):
        suc = model.getStarCount()
        assert not suc


def test_getStarCount_3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with (
        mock.patch.object(
            mw4.mountcontrol.model.Connection, "communicate", return_value=(True, ["100"], 1)
        ),
        mock.patch.object(model, "parseNumberStars", return_value=True),
    ):
        suc = model.getStarCount()
        assert suc


def test_getStars_0():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.numberStars = 0
    suc = model.getStars()
    assert suc


def test_getStars_1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.numberStars = 1
    with mock.patch.object(
        mw4.mountcontrol.model.Connection,
        "communicate",
        return_value=(False, ["100"], 1),
    ):
        suc = model.getStars()
        assert not suc


def test_getStars_2():
    obsSite = App().mount.obsSite
    obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)

    class Parent:
        host = None
        loggingTrace = False
        obsSite = obsSite

    model = Model(parent=Parent())
    model.numberStars = 1
    with mock.patch.object(
        mw4.mountcontrol.model.Connection,
        "communicate",
        return_value=(True, ["21:52:58.95,+08*56:10.1,   5.7,201"], 1),
    ):
        suc = model.getStars()
        assert suc


def test_pollStars_1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with mock.patch.object(model, "getStarCount", return_value=False):
        model.pollStars()


def test_pollStars_2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with (
        mock.patch.object(model, "getStarCount", return_value=True),
        mock.patch.object(model, "getStars", return_value=False),
    ):
        model.pollStars()


def test_pollStars_3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    with (
        mock.patch.object(model, "getStarCount", return_value=True),
        mock.patch.object(model, "getStars", return_value=True),
    ):
        model.pollStars()


#
#
# testing clearModel
#
#


def test_Model_clearAlign_ok():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    response = [""]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = model.clearModel()
        assert suc


def test_Model_clearAlign_not_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    response = [""]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = model.clearModel()
        assert not suc


#
#
# testing deletePoint
#
#


def test_Model_deletePoint_ok():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.numberStars = 5
    response = ["1"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = model.deletePoint(1)
        assert suc


def test_Model_deletePoint_not_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.numberStars = 5
    response = ["1#"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = model.deletePoint(1)
        assert not suc


def test_Model_deletePoint_not_ok4():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())
    model.numberStars = 5
    response = ["1"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = model.deletePoint(10)
        assert not suc


#
#
# testing storeName
#
#


def test_Model_storeName_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    response = ["1", "1"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = model.storeName("test")
        assert suc


def test_Model_storeName_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    response = ["0", "1"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = model.storeName("Test")
        assert suc


#
#
# testing loadName
#
#


def test_Model_loadName_ok():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = model.loadName("test")
        assert suc


def test_Model_loadName_not_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = model.loadName("test")
        assert not suc


#
#
# testing deleteName
#
#


def test_Model_deleteName_ok():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = model.deleteName("test")
        assert suc


def test_Model_deleteName_not_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = model.deleteName("test")
        assert not suc


#
#
# testing programModelFromStarList
#
#


def test_Model_programAlign_ok1():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    aPoint = ProgStar(
        Star(ra_hours=0, dec_degrees=0),
        Star(ra_hours=0, dec_degrees=0),
        Angle(hours=0),
        "e",
    )
    build = [aPoint]
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, ["1"], 1
        suc = model.programModelFromStarList(build)
        assert suc


def test_Model_programAlign_ok2():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    build = gatherData(1)
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, ["1"], 1
        suc = model.programModelFromStarList(build)
        assert suc


def test_Model_programAlign_ok3():
    class Parent:
        host = None
        loggingTrace = False

    model = Model(parent=Parent())

    build = gatherData(3)
    with mock.patch("mw4.mountcontrol.model.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, ["E"], 1
        suc = model.programModelFromStarList(build)
        assert suc


def gatherData(number):
    filename = "tests/testData/test.model"
    import json

    with open(filename) as infile:
        datas = json.load(infile)

    build = []
    for i, data in enumerate(datas):
        aPoint = ProgStar(
            Star(ra_hours=0, dec_degrees=0),
            Star(ra_hours=0, dec_degrees=0),
            Angle(hours=0),
            "e",
        )
        aPoint.mCoord = Star(ra_hours=data["raJNowM"], dec_degrees=data["decJNowM"])
        aPoint.sCoord = Star(ra_hours=data["raJNowS"], dec_degrees=data["decJNowS"])
        aPoint.pierside = data["pierside"]
        aPoint.sidereal = Angle(hours=data["siderealTime"])
        build.append(aPoint)
        if i == number - 1:
            break
    return build
