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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest
import unittest.mock as mock
import numpy

# external packages
import skyfield.api
from skyfield.api import wgs84, Star, Angle

# local imports
from mountcontrol.model import ModelStar, ProgStar
from mountcontrol.model import Model
from mountcontrol import obsSite
import mountcontrol

obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)


class ObsSite:
    location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)


class Parent:
    obsSite = ObsSite()


class TestConfigData(unittest.TestCase):
    def setUp(self):
        pass

    #
    #
    # testing the class Model and it's attribute
    #
    #

    def test_Model_altitudeError(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.altitudeError = "67"
        self.assertEqual(67, align.altitudeError.degrees)
        self.assertEqual(67, align._altitudeError.degrees)

    def test_Model_azimuthError(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.azimuthError = "67"
        self.assertEqual(67, align.azimuthError.degrees)
        self.assertEqual(67, align._azimuthError.degrees)

    def test_Model_polarError(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.polarError = "67"
        self.assertEqual(67, align.polarError.degrees)
        self.assertEqual(67, align._polarError.degrees)

    def test_Model_positionAngle1(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.positionAngle = "67"
        self.assertEqual(67, align.positionAngle.degrees)
        self.assertEqual(67, align._positionAngle.degrees)

    def test_Model_positionAngle2(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.positionAngle = skyfield.api.Angle(degrees=67)
        self.assertNotEqual(67, align.positionAngle)
        self.assertNotEqual(67, align._positionAngle)

    def test_Model_orthoError(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.orthoError = "67"
        self.assertEqual(67, align.orthoError.degrees)
        self.assertEqual(67, align._orthoError.degrees)

    def test_Model_altitudeTurns(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.altitudeTurns = "67"
        self.assertEqual(67, align.altitudeTurns)
        self.assertEqual(67, align._altitudeTurns)

    def test_Model_azimuthTurns(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.azimuthTurns = "67"
        self.assertEqual(67, align.azimuthTurns)
        self.assertEqual(67, align._azimuthTurns)

    def test_Model_terms(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.terms = "67"
        self.assertEqual(67, align.terms)
        self.assertEqual(67, align._terms)

    def test_Model_errorRMS(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.errorRMS = "67"
        self.assertEqual(67, align.errorRMS)
        self.assertEqual(67, align._errorRMS)

    def test_Model_numberStars_1(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.numberStars = "67"
        self.assertEqual(67, align.numberStars)
        self.assertEqual(67, align._numberStars)

    def test_Model_numberStars_2(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.numberStars = None
        self.assertEqual(None, align.numberStars)
        self.assertEqual(None, align._numberStars)

    def test_Model_numberNames_1(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.numberNames = "67"
        self.assertEqual(67, align.numberNames)
        self.assertEqual(67, align._numberNames)

    def test_Model_numberNames_2(self):
        class Parent:
            host = None

        align = Model(parent=Parent())
        align.numberNames = None
        self.assertEqual(None, align.numberNames)
        self.assertEqual(None, align._numberNames)

    def test_Model_starList1(self):
        p1 = "12:45:33.01"
        p2 = "+56*30:00.5"
        p3 = "1234.5"
        p4 = "90"
        p5 = obsSite
        modelStar1 = ModelStar(
            coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=1, obsSite=p5
        )

        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.starList = [modelStar1]
        self.assertEqual(len(model.starList), 1)

    def test_Model_starList2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.starList = "67"
        self.assertEqual(len(model.starList), 0)

    def test_Model_starList3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.starList = ["67", "78"]
        self.assertEqual(len(model.starList), 0)

    def test_add_del_Star(self):
        p1 = "12:45:33.01"
        p2 = "+56*30:00.5"
        p3 = "1234.5"
        p4 = "90"
        modelStar1 = ModelStar(
            coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=1, obsSite=obsSite
        )
        modelStar2 = ModelStar(
            coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=2, obsSite=obsSite
        )
        modelStar3 = ModelStar(
            coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=3, obsSite=obsSite
        )
        modelStar4 = ModelStar(
            coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=4, obsSite=obsSite
        )

        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.addStar(modelStar1)
        self.assertEqual(len(model.starList), 1)
        model.addStar(modelStar2)
        self.assertEqual(len(model.starList), 2)
        model.addStar(modelStar3)
        self.assertEqual(len(model.starList), 3)
        model.addStar(modelStar4)
        self.assertEqual(len(model.starList), 4)
        model.delStar(3)
        self.assertEqual(len(model.starList), 3)
        model.delStar(3)
        self.assertEqual(len(model.starList), 3)
        model.delStar(-1)
        self.assertEqual(len(model.starList), 3)
        model.delStar(1)
        self.assertEqual(len(model.starList), 2)

    def test_addStar_ok(self):
        class Parent:
            host = None
            obsSite = None

        model = Model(parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addStar("12:45:33.01,+56*30:00.5,1234.5,90,1")
        self.assertEqual(len(model.starList), 1)

    def test_StarList_iteration(self):
        p1 = "12:45:33.01"
        p2 = "+56*30:00.5"

        class Parent:
            host = None

        model = Model(parent=Parent())

        for i in range(0, 10):
            model.addStar(
                ModelStar(
                    coord=(p1, p2),
                    errorRMS=str(i * i),
                    errorAngle=str(i * i),
                    number=str(i),
                    obsSite=obsSite,
                )
            )

        self.assertEqual(len(model.starList), 10)
        for i, star in enumerate(model.starList):
            self.assertEqual(i, star.number)
            self.assertEqual(i * i, star.errorRMS)

    def test_StarList_checkStarListOK(self):
        class Parent:
            host = None
            obsSite = None

        model = Model(parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addStar("12:45:33.01,+56*30:00.5,1234.5,90,1")
        model.numberStars = 1
        self.assertTrue(model.checkStarListOK())

    def test_StarList_checkStarList_not_OK1(self):
        class Parent:
            host = None
            obsSite = None

        model = Model(parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addStar("12:45:33.01,+56*30:00.5,1234.5,90,1")
        model.numberStars = 2
        self.assertFalse(model.checkStarListOK())

        class Parent:
            host = None
            obsSite = None

        model = Model(parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addStar("12:45:33.01,+56*30:00.5,1234.5,90,1")
        self.assertFalse(model.checkStarListOK())

    def test_Model_nameList1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.nameList = 67
        self.assertEqual(len(model.nameList), 0)

    def test_Model_nameList2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.nameList = ["67"]
        self.assertEqual(len(model.nameList), 1)

    def test_Model_nameList3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.nameList = ["67", "78"]
        self.assertEqual(len(model.nameList), 2)

    def test_Model_nameList4(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.nameList = ["67", 67]
        self.assertEqual(len(model.nameList), 0)

    def test_add_del_Name(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.addName("the first one")
        self.assertEqual(len(model.nameList), 1)
        model.addName("the second one")
        self.assertEqual(len(model.nameList), 2)
        model.addName("the third one")
        self.assertEqual(len(model.nameList), 3)
        model.addName("the fourth one")
        self.assertEqual(len(model.nameList), 4)
        model.delName(3)
        self.assertEqual(len(model.nameList), 3)
        model.delName(3)
        self.assertEqual(len(model.nameList), 3)
        model.delName(-1)
        self.assertEqual(len(model.nameList), 3)
        model.delName(1)
        self.assertEqual(len(model.nameList), 2)

    def test_addName_not_ok(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.addName(45)
        self.assertEqual(len(model.nameList), 0)

    def test_NameList_iteration(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        for i in range(0, 10):
            model.addName("this is the {0}.th name".format(i))
        self.assertEqual(len(model.nameList), 10)
        for i, name in enumerate(model.nameList):
            self.assertEqual("this is the {0}.th name".format(i), name)

    def test_StarList_checkNameListOK(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addName("12:45:33.01,+56*30:00.5,1234.5,90,1")
        model.numberNames = 1
        self.assertTrue(model.checkNameListOK())

    def test_StarList_checkNameList_not_OK1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addName("12:45:33.01,+56*30:00.5,1234.5,90,1")
        model.numberNames = 2
        self.assertFalse(model.checkNameListOK())

    def test_StarList_checkNameList_not_OK2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addName("12:45:33.01,+56*30:00.5,1234.5,90,1")
        self.assertFalse(model.checkNameListOK())

    #
    #
    # testing the specific QCI behaviour in Model class attributes
    #
    #

    def test_errorRMS_HPS(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.errorRMS = "36.8"
        self.assertEqual(36.8, model.errorRMS)
        self.assertEqual(36.8, model._errorRMS)

    def test_errorRMS_HPS_empty(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.errorRMS = "E"
        self.assertIsNone(model.errorRMS)

    def test_errorRMS_HPS_float(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.errorRMS = 36.8
        self.assertEqual(36.8, model.errorRMS)

    def test_errorRMS_HPS_int(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.errorRMS = 36
        self.assertEqual(36.0, model.errorRMS)

    def test_errorRMS_HPS_tuple(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.errorRMS = (36.8, 1.0)
        self.assertIsNone(model.errorRMS)

    def test_errorRMS_QCI(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.errorRMS = ""
        self.assertIsNone(model.errorRMS)

    def test_errorTerms_QCI(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.terms = ""
        self.assertIsNone(model.terms)

    #
    #
    # testing the class AlignStar and it's attribute setters
    #
    #

    def test_AlignStar_coord1(self):
        p1 = "12:45:33.01"
        p2 = "+56*30:00.5"
        p3 = "1234.5"
        p4 = "90"
        p5 = obsSite
        alignStar = ModelStar(coord=(p1, p2), errorRMS=p3, errorAngle=p4, number=1, obsSite=p5)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[1], 45, 6)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[2], 33.01, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[1], 30, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[2], 0.5, 6)

    def test_AlignStar_coord2(self):
        star = skyfield.api.Star(ra_hours=12.55, dec_degrees=56.55)
        p3 = "1234.5"
        p4 = "90"
        alignStar = ModelStar(
            coord=star, errorRMS=p3, errorAngle=p4, number=1, obsSite=obsSite
        )
        self.assertAlmostEqual(alignStar.coord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[1], 33, 6)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[2], 0, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[1], 33, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[2], 0, 6)

    def test_AlignStar_coord_not_ok1(self):
        p1 = "12:45:33.01"
        p2 = "+56*30:00.5"
        p3 = "1234.5"
        alignStar = ModelStar(coord=(p1, p2, p3))
        self.assertIsNone(alignStar.coord)

    def test_AlignStar_coord_not_ok2(self):
        p1 = "12:45:33.01"
        p2 = "+56*30:00.5"
        p3 = "1234.5"
        alignStar = ModelStar(coord=[p1, p2, p3])
        self.assertIsNone(alignStar.coord)

    def test_AlignStar_coord_not_ok3(self):
        alignStar = ModelStar(coord=56)
        self.assertIsNone(alignStar.coord)

    def test_AlignStar_coord_not_ok4(self):
        p1 = "12:45:33.01"
        alignStar = ModelStar(coord=(p1, 67))
        self.assertIsNone(alignStar.coord)

    def test_AlignStar_number(self):
        alignStar = ModelStar()
        alignStar.number = 6
        self.assertEqual(6, alignStar.number)

    def test_AlignStar_number1(self):
        alignStar = ModelStar()
        alignStar.number = "6"
        self.assertEqual(6, alignStar.number)

    def test_AlignStar_errorAngle(self):
        alignStar = ModelStar()
        alignStar.errorAngle = 50
        self.assertEqual(50, alignStar.errorAngle.degrees)

    def test_AlignStar_errorRMS(self):
        alignStar = ModelStar()
        alignStar.errorRMS = 6
        self.assertEqual(6, alignStar.errorRMS)

    def test_AlignStar_error_DEC_RA(self):
        alignStar = ModelStar()
        alignStar.errorRMS = 6
        alignStar.errorAngle = 50
        ra = 6 * numpy.sin(50 * numpy.pi * 2 / 360)
        dec = 6 * numpy.cos(50 * numpy.pi * 2 / 360)
        self.assertAlmostEqual(ra, alignStar.errorRA().degrees)
        self.assertAlmostEqual(dec, alignStar.errorDEC().degrees)

    def test_Model_parseNumberName_ok(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["5"]
        suc = model.parseNumberNames(response, 1)
        self.assertTrue(suc)

    def test_Model_parseNumberName_not_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["df"]
        suc = model.parseNumberNames(response, 1)
        self.assertTrue(suc)

    def test_Model_parseNumberName_not_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = [""]
        suc = model.parseNumberNames(response, 1)
        self.assertTrue(suc)

    def test_Model_parseNumberName_not_ok3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["5a"]
        suc = model.parseNumberNames(response, 1)
        self.assertTrue(suc)

    def test_Model_parseNumberName_not_ok4(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["5", "4"]
        suc = model.parseNumberNames(response, 1)
        self.assertFalse(suc)

    def test_Model_parseNumberName_not_ok5(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["5", "g"]
        suc = model.parseNumberNames(response, 1)
        self.assertFalse(suc)

    #
    #
    # testing modelNames
    #
    #

    def test_Model_parseNames_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["test"]
        suc = model.parseNames(response, 1)
        self.assertTrue(suc)

    def test_Model_parseNames_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["sd", "", None]
        suc = model.parseNames(response, 3)
        self.assertTrue(suc)

    def test_Model_parseNumberNames_ok3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["5"]
        suc = model.parseNumberNames(response, 1)
        self.assertTrue(suc)

    def test_Model_parseNames_not_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["sd"]
        suc = model.parseNames(response, 3)
        self.assertFalse(suc)

    def test_Model_parseNumberNames_not_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["sd"]
        suc = model.parseNumberNames(response, 1)
        self.assertTrue(suc)

    def test_Model_parseNumberNames_not_ok3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["5", "6"]
        suc = model.parseNumberNames(response, 2)
        self.assertFalse(suc)

    def test_getNameCount_1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(False, ["100"], 1),
        ):
            suc = model.getNameCount()
            assert not suc

    def test_getNameCount_2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(True, ["100"], 1),
        ):
            suc = model.getNameCount()
            assert suc

    def test_getNames_1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.numberNames = 1
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(False, ["100"], 1),
        ):
            suc = model.getNames()
            assert not suc

    def test_getNames_2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.numberNames = 1
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(True, ["100"], 1),
        ):
            suc = model.getNames()
            assert suc

    def test_pollNames_1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(model, "getNameCount", return_value=False):
            suc = model.pollNames()
            assert not suc

    def test_pollNames_2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(model, "getNameCount", return_value=True):
            with mock.patch.object(model, "getNames", return_value=False):
                suc = model.pollNames()
            assert not suc

    def test_pollNames_3(self):
        class Parent:
            host = None

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

    def test_Model_parseNumberStars_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["0", "E"]
        suc = model.parseNumberStars(response, 2)
        self.assertTrue(suc)

    def test_Model_parseNumberStars_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = [
            "1",
            "023.8311, +24.8157, 29.8580, 227.45, -12.9985, +26.98, -08.97, 11, 97751.6",
        ]
        suc = model.parseNumberStars(response, 2)
        self.assertTrue(suc)
        assert model.azimuthError.degrees == 23.8311
        assert model.altitudeError.degrees == 24.8157
        assert model.polarError.degrees == 29.8580
        assert model.positionAngle.degrees == 227.45
        assert model.orthoError.degrees == -12.9985
        assert model.azimuthTurns == 26.98
        assert model.altitudeTurns == -08.97
        assert model.errorRMS == 97751.6
        assert model.terms == 11

    def test_Model_parseNumberStars_not_ok0(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["4", "E"]
        suc = model.parseNumberStars(response, 1)
        self.assertFalse(suc)

    def test_Model_parseNumberStars_not_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["4"]
        suc = model.parseNumberStars(response, 1)
        self.assertFalse(suc)

    def test_Model_parseNumberStars_not_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["4", "4, 4, 4"]
        suc = model.parseNumberStars(response, 2)
        self.assertFalse(suc)

    def test_Model_parseNumberStars_not_ok3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        response = ["4", "4"]
        suc = model.parseNumberStars(response, 2)
        self.assertFalse(suc)

    def test_Model_parseStars_ok(self):
        class Parent:
            host = None
            obsSite = None

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
        self.assertTrue(suc)
        self.assertEqual(len(model.starList), 11)

    def test_Model_parseStars_not_ok1(self):
        class Parent:
            host = None
            obsSite = None

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
        self.assertFalse(suc)
        self.assertEqual(len(model.starList), 0)

    def test_getStarCount_1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(False, ["100"], 1),
        ):
            with mock.patch.object(model, "parseNumberStars", return_value=False):
                suc = model.getStarCount()
                assert not suc

    def test_getStarCount_2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(True, ["100"], 1),
        ):
            with mock.patch.object(model, "parseNumberStars", return_value=False):
                suc = model.getStarCount()
                assert not suc

    def test_getStarCount_3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(True, ["100"], 1),
        ):
            with mock.patch.object(model, "parseNumberStars", return_value=True):
                suc = model.getStarCount()
                assert suc

    def test_getStars_0(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.numberStars = 0
        suc = model.getStars()
        assert suc

    def test_getStars_1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.numberStars = 1
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(False, ["100"], 1),
        ):
            suc = model.getStars()
            assert not suc

    def test_getStars_2(self):
        class Parent:
            host = None
            obsSite = None

        model = Model(parent=Parent())
        model.numberStars = 1
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(True, ["21:52:58.95,+08*56:10.1,   5.7,201"], 1),
        ):
            suc = model.getStars()
            assert suc

    def test_pollStars_1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(model, "getStarCount", return_value=False):
            suc = model.pollStars()
            assert not suc

    def test_pollStars_2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(model, "getStarCount", return_value=True):
            with mock.patch.object(model, "getStars", return_value=False):
                suc = model.pollStars()
            assert not suc

    def test_pollStars_3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(model, "getStarCount", return_value=True):
            with mock.patch.object(model, "getStars", return_value=True):
                suc = model.pollStars()
            assert suc

    #
    #
    # testing pollCount
    #
    #

    def test_Model_pollCount_1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(True, ["5", "6"], 2),
        ):
            suc = model.pollCount()
            assert suc
            assert model.numberNames == 5
            assert model.numberStars == 6

    def test_Model_pollCount_2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(False, ["5", "6"], 2),
        ):
            suc = model.pollCount()
            assert not suc

    def test_Model_pollCount_3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(True, ["5", "6"], 3),
        ):
            suc = model.pollCount()
            assert not suc

    def test_Model_pollCount_4(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        with mock.patch.object(
            mountcontrol.model.Connection,
            "communicate",
            return_value=(True, ["5", "6", "7"], 3),
        ):
            suc = model.pollCount()
            assert not suc

    #
    #
    # testing clearModel
    #
    #

    def test_Model_clearAlign_ok(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        response = [""]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.clearModel()
            self.assertTrue(suc)

    def test_Model_clearAlign_not_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        response = [""]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = model.clearModel()
            self.assertFalse(suc)

    #
    #
    # testing deletePoint
    #
    #

    def test_Model_deletePoint_ok(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.numberStars = 5
        response = ["1"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deletePoint(1)
            self.assertTrue(suc)

    def test_Model_deletePoint_not_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.numberStars = 5
        response = ["1#"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = model.deletePoint(1)
            self.assertFalse(suc)

    def test_Model_deletePoint_not_ok4(self):
        class Parent:
            host = None

        model = Model(parent=Parent())
        model.numberStars = 5
        response = ["1"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deletePoint(10)
            self.assertFalse(suc)

    #
    #
    # testing storeName
    #
    #

    def test_Model_storeName_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        response = ["1", "1"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = model.storeName("test")
            self.assertTrue(suc)

    def test_Model_storeName_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        response = ["0", "1"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = model.storeName("Test")
            self.assertTrue(suc)

    #
    #
    # testing loadName
    #
    #

    def test_Model_loadName_ok(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        response = ["1"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.loadName("test")
            self.assertTrue(suc)

    def test_Model_loadName_not_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        response = ["1"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = model.loadName("test")
            self.assertFalse(suc)

    #
    #
    # testing deleteName
    #
    #

    def test_Model_deleteName_ok(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        response = ["1"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deleteName("test")
            self.assertTrue(suc)

    def test_Model_deleteName_not_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        response = ["1"]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = model.deleteName("test")
            self.assertFalse(suc)

    #
    #
    # testing programModelFromStarList
    #
    #

    def test_Model_programAlign_ok1(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        aPoint = ProgStar(
            Star(ra_hours=0, dec_degrees=0),
            Star(ra_hours=0, dec_degrees=0),
            Angle(hours=0),
            "e",
        )
        build = [aPoint]
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, ["1"], 1
            suc = model.programModelFromStarList(build)
            self.assertTrue(suc)

    def test_Model_programAlign_ok2(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        build = self.gatherData(1)
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, ["1"], 1
            suc = model.programModelFromStarList(build)
            self.assertTrue(suc)

    def test_Model_programAlign_ok3(self):
        class Parent:
            host = None

        model = Model(parent=Parent())

        build = self.gatherData(3)
        with mock.patch("mountcontrol.model.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, ["E"], 1
            suc = model.programModelFromStarList(build)
            self.assertTrue(suc)

    @staticmethod
    def gatherData(number):
        filename = "tests/testData/test.model"
        import json

        with open(filename, "r") as infile:
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
