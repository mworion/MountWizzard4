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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest
import unittest.mock as mock
import numpy

# external packages
import skyfield.api
from skyfield.api import wgs84

# local imports
from mountcontrol.model import ModelStar, AlignStar
from mountcontrol.model import Model
from mountcontrol import obsSite
import mountcontrol

obsSite.location = wgs84.latlon(latitude_degrees=0,
                                longitude_degrees=0,
                                elevation_m=0)


class ObsSite:
    location = wgs84.latlon(latitude_degrees=0,
                            longitude_degrees=0,
                            elevation_m=0)


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
        align = Model()
        align.altitudeError = '67'
        self.assertEqual(67, align.altitudeError.degrees)
        self.assertEqual(67, align._altitudeError.degrees)

    def test_Model_azimuthError(self):
        align = Model()
        align.azimuthError = '67'
        self.assertEqual(67, align.azimuthError.degrees)
        self.assertEqual(67, align._azimuthError.degrees)

    def test_Model_polarError(self):
        align = Model()
        align.polarError = '67'
        self.assertEqual(67, align.polarError.degrees)
        self.assertEqual(67, align._polarError.degrees)

    def test_Model_positionAngle1(self):
        align = Model()
        align.positionAngle = '67'
        self.assertEqual(67, align.positionAngle.degrees)
        self.assertEqual(67, align._positionAngle.degrees)

    def test_Model_positionAngle2(self):
        align = Model()
        align.positionAngle = skyfield.api.Angle(degrees=67)
        self.assertNotEqual(67, align.positionAngle)
        self.assertNotEqual(67, align._positionAngle)

    def test_Model_orthoError(self):
        align = Model()
        align.orthoError = '67'
        self.assertEqual(67, align.orthoError.degrees)
        self.assertEqual(67, align._orthoError.degrees)

    def test_Model_altitudeTurns(self):
        align = Model()
        align.altitudeTurns = '67'
        self.assertEqual(67, align.altitudeTurns)
        self.assertEqual(67, align._altitudeTurns)

    def test_Model_azimuthTurns(self):
        align = Model()
        align.azimuthTurns = '67'
        self.assertEqual(67, align.azimuthTurns)
        self.assertEqual(67, align._azimuthTurns)

    def test_Model_terms(self):
        align = Model()
        align.terms = '67'
        self.assertEqual(67, align.terms)
        self.assertEqual(67, align._terms)

    def test_Model_errorRMS(self):
        align = Model()
        align.errorRMS = '67'
        self.assertEqual(67, align.errorRMS)
        self.assertEqual(67, align._errorRMS)

    def test_Model_numberStars(self):
        align = Model()
        align.numberStars = '67'
        self.assertEqual(67, align.numberStars)
        self.assertEqual(67, align._numberStars)

    def test_Model_numberNames(self):
        align = Model()
        align.numberNames = '67'
        self.assertEqual(67, align.numberNames)
        self.assertEqual(67, align._numberNames)

    def test_Model_starList1(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        p4 = '90'
        p5 = obsSite
        modelStar1 = ModelStar(coord=(p1, p2),
                               errorRMS=p3,
                               errorAngle=p4,
                               number=1,
                               obsSite=p5)

        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.starList = [modelStar1]
        self.assertEqual(len(model.starList), 1)

    def test_Model_starList2(self):
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.starList = '67'
        self.assertEqual(len(model.starList), 0)

    def test_Model_starList3(self):
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.starList = ['67', '78']
        self.assertEqual(len(model.starList), 0)

    def test_add_del_Star(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        p4 = '90'
        modelStar1 = ModelStar(coord=(p1, p2), errorRMS=p3,
                               errorAngle=p4, number=1,
                               obsSite=obsSite)
        modelStar2 = ModelStar(coord=(p1, p2), errorRMS=p3,
                               errorAngle=p4, number=2,
                               obsSite=obsSite)
        modelStar3 = ModelStar(coord=(p1, p2), errorRMS=p3,
                               errorAngle=p4, number=3,
                               obsSite=obsSite)
        modelStar4 = ModelStar(coord=(p1, p2), errorRMS=p3,
                               errorAngle=p4, number=4,
                               obsSite=obsSite)

        model = Model(host=None, parent=Parent())

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
        model = Model(host=None, parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addStar('12:45:33.01,+56*30:00.5,1234.5,90,1')
        self.assertEqual(len(model.starList), 1)

    def test_addStar_not_ok1(self):
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.addStar(67)
        self.assertEqual(len(model.starList), 0)

    def test_addStar_not_ok2(self):
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.starList), 0)
        model.addStar('test')
        self.assertEqual(len(model.starList), 0)

    def test_StarList_iteration(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        model = Model(host=None, parent=Parent())

        for i in range(0, 10):
            model.addStar(ModelStar(coord=(p1, p2),
                                    errorRMS=str(i*i),
                                    errorAngle=str(i*i),
                                    number=str(i),
                                    obsSite=obsSite))

        self.assertEqual(len(model.starList), 10)
        for i, star in enumerate(model.starList):
            self.assertEqual(i,
                             star.number)
            self.assertEqual(i*i,
                             star.errorRMS)

    def test_StarList_checkStarListOK(self):
        model = Model(host=None, parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addStar('12:45:33.01,+56*30:00.5,1234.5,90,1')
        model.numberStars = 1
        self.assertEqual(True, model.checkStarListOK())

    def test_StarList_checkStarList_not_OK1(self):
        model = Model(host=None, parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addStar('12:45:33.01,+56*30:00.5,1234.5,90,1')
        model.numberStars = 2
        self.assertEqual(False, model.checkStarListOK())

    def test_StarList_checkStarList_not_OK2(self):
        model = Model(host=None, parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addStar('12:45:33.01,+56*30:00.5,1234.5,90,1')
        self.assertEqual(False, model.checkStarListOK())

    def test_Model_nameList1(self):

        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.nameList = 67
        self.assertEqual(len(model.nameList), 0)

    def test_Model_nameList2(self):
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.nameList = ['67']
        self.assertEqual(len(model.nameList), 1)

    def test_Model_nameList3(self):
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.nameList = ['67', '78']
        self.assertEqual(len(model.nameList), 2)

    def test_Model_nameList4(self):
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.nameList = ['67', 67]
        self.assertEqual(len(model.nameList), 0)

    def test_add_del_Name(self):
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.addName('the first one')
        self.assertEqual(len(model.nameList), 1)
        model.addName('the second one')
        self.assertEqual(len(model.nameList), 2)
        model.addName('the third one')
        self.assertEqual(len(model.nameList), 3)
        model.addName('the fourth one')
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
        model = Model(host=None, parent=Parent())

        self.assertEqual(len(model.nameList), 0)
        model.addName(45)
        self.assertEqual(len(model.nameList), 0)

    def test_NameList_iteration(self):
        model = Model(host=None, parent=Parent())

        for i in range(0, 10):
            model.addName('this is the {0}.th name'.format(i))
        self.assertEqual(len(model.nameList), 10)
        for i, name in enumerate(model.nameList):
            self.assertEqual('this is the {0}.th name'.format(i),
                             name)

    def test_StarList_checkNameListOK(self):
        model = Model(host=None, parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addName('12:45:33.01,+56*30:00.5,1234.5,90,1')
        model.numberNames = 1
        self.assertEqual(True, model.checkNameListOK())

    def test_StarList_checkNameList_not_OK1(self):
        model = Model(host=None, parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addName('12:45:33.01,+56*30:00.5,1234.5,90,1')
        model.numberNames = 2
        self.assertEqual(False, model.checkNameListOK())

    def test_StarList_checkNameList_not_OK2(self):
        model = Model(host=None, parent=Parent())
        self.assertEqual(len(model.starList), 0)
        model.addName('12:45:33.01,+56*30:00.5,1234.5,90,1')
        self.assertEqual(False, model.checkNameListOK())
    #
    #
    # testing the specific QCI behaviour in Model class attributes
    #
    #

    def test_errorRMS_HPS(self):
        model = Model(host=None, parent=Parent())
        model.errorRMS = '36.8'
        self.assertEqual(36.8, model.errorRMS)
        self.assertEqual(36.8, model._errorRMS)

    def test_errorRMS_HPS_empty(self):
        model = Model(host=None, parent=Parent())
        model.errorRMS = 'E'
        self.assertEqual(None, model.errorRMS)

    def test_errorRMS_HPS_float(self):
        model = Model(host=None, parent=Parent())
        model.errorRMS = 36.8
        self.assertEqual(36.8, model.errorRMS)

    def test_errorRMS_HPS_int(self):
        model = Model(host=None, parent=Parent())
        model.errorRMS = 36
        self.assertEqual(36.0, model.errorRMS)

    def test_errorRMS_HPS_tuple(self):
        model = Model(host=None, parent=Parent())
        model.errorRMS = (36.8, 1.0)
        self.assertEqual(None, model.errorRMS)

    def test_errorRMS_QCI(self):
        model = Model(host=None, parent=Parent())
        model.errorRMS = ''
        self.assertEqual(None, model.errorRMS)

    def test_errorTerms_QCI(self):
        model = Model(host=None, parent=Parent())
        model.terms = ''
        self.assertEqual(None, model.terms)
    #
    #
    # testing the class AlignStar and it's attribute setters
    #
    #

    def test_AlignStar_coord1(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        p4 = '90'
        p5 = obsSite
        alignStar = ModelStar(coord=(p1, p2), errorRMS=p3,
                              errorAngle=p4, number=1,
                              obsSite=p5)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[1], 45, 6)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[2], 33.01, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[1], 30, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[2], 0.5, 6)

    def test_AlignStar_coord2(self):
        star = skyfield.api.Star(ra_hours=12.55, dec_degrees=56.55)
        p3 = '1234.5'
        p4 = '90'
        alignStar = ModelStar(coord=star, errorRMS=p3,
                              errorAngle=p4, number=1,
                              obsSite=obsSite)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[1], 33, 6)
        self.assertAlmostEqual(alignStar.coord.ra.hms()[2], 0, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[1], 33, 6)
        self.assertAlmostEqual(alignStar.coord.dec.dms()[2], 0, 6)

    def test_AlignStar_coord_not_ok1(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        alignStar = ModelStar(coord=(p1, p2, p3))
        self.assertEqual(None, alignStar.coord)

    def test_AlignStar_coord_not_ok2(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        alignStar = ModelStar(coord=[p1, p2, p3])
        self.assertEqual(None, alignStar.coord)

    def test_AlignStar_coord_not_ok3(self):
        alignStar = ModelStar(coord=56)
        self.assertEqual(None, alignStar.coord)

    def test_AlignStar_coord_not_ok4(self):
        p1 = '12:45:33.01'
        alignStar = ModelStar(coord=(p1, 67))
        self.assertEqual(None, alignStar.coord)

    def test_AlignStar_number(self):
        alignStar = ModelStar()
        alignStar.number = 6
        self.assertEqual(6, alignStar.number)

    def test_AlignStar_number1(self):
        alignStar = ModelStar()
        alignStar.number = '6'
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
        self.assertAlmostEqual(ra, alignStar.errorRA())
        self.assertAlmostEqual(dec, alignStar.errorDEC())

    def test_Model_parseNumberName_ok(self):
        model = Model(host=None, parent=Parent())
        response = ['5']
        suc = model.parseNumberNames(response, 1)
        self.assertEqual(True, suc)

    def test_Model_parseNumberName_not_ok1(self):
        model = Model(host=None, parent=Parent())
        response = ['df']
        suc = model.parseNumberNames(response, 1)
        self.assertEqual(True, suc)

    def test_Model_parseNumberName_not_ok2(self):
        model = Model(host=None, parent=Parent())
        response = ['']
        suc = model.parseNumberNames(response, 1)
        self.assertEqual(True, suc)

    def test_Model_parseNumberName_not_ok3(self):
        model = Model(host=None, parent=Parent())
        response = ['5a']
        suc = model.parseNumberNames(response, 1)
        self.assertEqual(True, suc)

    def test_Model_parseNumberName_not_ok4(self):
        model = Model(host=None, parent=Parent())
        response = ['5', '4']
        suc = model.parseNumberNames(response, 1)
        self.assertEqual(False, suc)

    def test_Model_parseNumberName_not_ok5(self):
        model = Model(host=None, parent=Parent())
        response = ['5', 'g']
        suc = model.parseNumberNames(response, 1)
        self.assertEqual(False, suc)
    #
    #
    # testing modelNames
    #
    #

    def test_Model_parseNames_ok1(self):
        model = Model(host=None, parent=Parent())
        response = ['test']
        suc = model.parseNames(response, 1)
        self.assertEqual(True, suc)

    def test_Model_parseNames_ok2(self):
        model = Model(host=None, parent=Parent())
        response = ['sd', '', None]
        suc = model.parseNames(response, 3)
        self.assertEqual(True, suc)

    def test_Model_parseNumberNames_ok3(self):
        model = Model(host=None, parent=Parent())
        response = ['5']
        suc = model.parseNumberNames(response, 1)
        self.assertEqual(True, suc)

    def test_Model_parseNames_not_ok1(self):
        model = Model(host=None, parent=Parent())
        response = ['sd']
        suc = model.parseNames(response, 3)
        self.assertEqual(False, suc)

    def test_Model_parseNumberNames_not_ok2(self):
        model = Model(host=None, parent=Parent())
        response = ['sd']
        suc = model.parseNumberNames(response, 1)
        self.assertEqual(True, suc)

    def test_Model_parseNumberNames_not_ok3(self):
        model = Model(host=None, parent=Parent())
        response = ['5', '6']
        suc = model.parseNumberNames(response, 2)
        self.assertEqual(False, suc)

    def test_getNameCount_1(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(False, ['100'], 1)):
            suc = model.getNameCount()
            assert not suc

    def test_getNameCount_2(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(True, ['100'], 1)):
            suc = model.getNameCount()
            assert suc

    def test_getNames_1(self):
        model = Model(host=None, parent=Parent())
        model.numberNames = 1
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(False, ['100'], 1)):
            suc = model.getNames()
            assert not suc

    def test_getNames_2(self):
        model = Model(host=None, parent=Parent())
        model.numberNames = 1
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(True, ['100'], 1)):
            suc = model.getNames()
            assert suc

    def test_pollNames_1(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(model,
                               'getNameCount',
                               return_value=False):
            suc = model.pollNames()
            assert not suc

    def test_pollNames_2(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(model,
                               'getNameCount',
                               return_value=True):
            with mock.patch.object(model,
                                   'getNames',
                                   return_value=False):
                suc = model.pollNames()
            assert not suc

    def test_pollNames_3(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(model,
                               'getNameCount',
                               return_value=True):
            with mock.patch.object(model,
                                   'getNames',
                                   return_value=True):
                suc = model.pollNames()
            assert suc

    #
    #
    # testing model stars
    #
    #

    def test_Model_parseNumberStars_ok1(self):
        model = Model(host=None, parent=Parent())
        response = ['0', 'E']
        suc = model.parseNumberStars(response, 2)
        self.assertEqual(True, suc)

    def test_Model_parseNumberStars_ok2(self):
        model = Model(host=None, parent=Parent())
        response = \
            ['1', '023.8311, +24.8157, 29.8580, 227.45, -12.9985, +26.98, -08.97, 11, 97751.6']
        suc = model.parseNumberStars(response, 2)
        self.assertEqual(True, suc)

    def test_Model_parseNumberStars_not_ok0(self):
        model = Model(host=None, parent=Parent())
        response = ['4', 'E']
        suc = model.parseNumberStars(response, 1)
        self.assertEqual(False, suc)

    def test_Model_parseNumberStars_not_ok1(self):
        model = Model(host=None, parent=Parent())
        response = ['4']
        suc = model.parseNumberStars(response, 1)
        self.assertEqual(False, suc)

    def test_Model_parseNumberStars_not_ok2(self):
        model = Model(host=None, parent=Parent())
        response = ['4', '4, 4, 4']
        suc = model.parseNumberStars(response, 2)
        self.assertEqual(False, suc)

    def test_Model_parseNumberStars_not_ok3(self):
        model = Model(host=None, parent=Parent())
        response = ['4', '4']
        suc = model.parseNumberStars(response, 2)
        self.assertEqual(False, suc)

    def test_Model_parseStars_ok(self):
        model = Model(host=None, parent=Parent())
        response = [
            '21:52:58.95,+08*56:10.1,   5.7,201',
            '21:06:10.79,+45*20:52.8,  12.1,329',
            '23:13:58.02,+38*48:18.8,  31.0,162',
            '17:43:41.26,+59*15:30.7,   8.4,005',
            '20:36:01.52,+62*39:32.4,  19.5,138',
            '03:43:11.04,+19*06:30.3,  22.6,199',
            '05:03:10.81,+38*14:22.2,  20.1,340',
            '04:12:55.39,+49*14:00.2,  17.1,119',
            '06:57:55.11,+61*40:26.8,   9.8,038',
            '22:32:24.00,+28*00:23.6,  42.1,347',
            '13:09:03.49,+66*24:40.5,  13.9,177',
        ]
        suc = model.parseStars(response, 11)
        self.assertEqual(True, suc)
        self.assertEqual(len(model.starList), 11)

    def test_Model_parseStars_not_ok1(self):
        model = Model(host=None, parent=Parent())
        response = [
            '21:52:58.95,+08*56:10.1,   5.7,201',
            '21:06:10.79,+45*20:52.8,  12.1,329',
            '23:13:58.02,+38*48:18.8,  31.0,162',
            '06:57:55.11,+61*40:26.8,   9.8,038',
            '22:32:24.00,+28*00:23.6,  42.1,347',
            '13:09:03.49,+66*24:40.5,  13.9,177',
        ]
        suc = model.parseStars(response, 4)
        self.assertEqual(False, suc)
        self.assertEqual(len(model.starList), 0)

    def test_Model_parseStars_not_ok2(self):
        model = Model(host=None, parent=Parent())
        response = [
            '21:52:58.95,+08*56:10.1,   5.7,201',
            ''
        ]
        suc = model.parseStars(response, 2)
        self.assertEqual(True, suc)
        self.assertEqual(len(model.starList), 1)

    def test_getStarCount_1(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(False, ['100'], 1)):
            with mock.patch.object(model,
                                   'parseNumberStars',
                                   return_value=False):
                suc = model.getStarCount()
                assert not suc

    def test_getStarCount_2(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(True, ['100'], 1)):
            with mock.patch.object(model,
                                   'parseNumberStars',
                                   return_value=False):
                suc = model.getStarCount()
                assert not suc

    def test_getStarCount_3(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(True, ['100'], 1)):
            with mock.patch.object(model,
                                   'parseNumberStars',
                                   return_value=True):
                suc = model.getStarCount()
                assert suc

    def test_getStars_0(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 0
        suc = model.getStars()
        assert suc

    def test_getStars_1(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 1
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(False, ['100'], 1)):
            suc = model.getStars()
            assert not suc

    def test_getStars_2(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 1
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(True, ['100'], 1)):
            suc = model.getStars()
            assert suc

    def test_pollStars_1(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(model,
                               'getStarCount',
                               return_value=False):
            suc = model.pollStars()
            assert not suc

    def test_pollStars_2(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(model,
                               'getStarCount',
                               return_value=True):
            with mock.patch.object(model,
                                   'getStars',
                                   return_value=False):
                suc = model.pollStars()
            assert not suc

    def test_pollStars_3(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(model,
                               'getStarCount',
                               return_value=True):
            with mock.patch.object(model,
                                   'getStars',
                                   return_value=True):
                suc = model.pollStars()
            assert suc

    #
    #
    # testing pollCount
    #
    #

    def test_Model_pollCount_1(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(True, ['5', '6'], 2)):
            suc = model.pollCount()
            assert suc
            assert model.numberNames == 5
            assert model.numberStars == 6

    def test_Model_pollCount_2(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(False, ['5', '6'], 2)):
            suc = model.pollCount()
            assert not suc

    def test_Model_pollCount_3(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(True, ['5', '6'], 3)):
            suc = model.pollCount()
            assert not suc

    def test_Model_pollCount_4(self):
        model = Model(host=None, parent=Parent())
        with mock.patch.object(mountcontrol.model.Connection,
                               'communicate',
                               return_value=(True, ['5', '6', '7'], 3)):
            suc = model.pollCount()
            assert not suc

    #
    #
    # testing clearAlign
    #
    #

    def test_Model_clearAlign_ok(self):
        model = Model(host=None, parent=Parent())

        response = ['']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.clearAlign()
            self.assertEqual(True, suc)

    def test_Model_clearAlign_not_ok1(self):
        model = Model(host=None, parent=Parent())

        response = ['']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = model.clearAlign()
            self.assertEqual(False, suc)

    def test_Model_clearAlign_not_ok2(self):
        model = Model(host=None, parent=Parent())

        response = [' ']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.clearAlign()
            self.assertEqual(False, suc)

    #
    #
    # testing deletePoint
    #
    #

    def test_Model_deletePoint_ok(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 5
        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deletePoint(1)
            self.assertEqual(True, suc)

    def test_Model_deletePoint_not_ok1(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 5
        response = ['1#']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = model.deletePoint(1)
            self.assertEqual(False, suc)

    def test_Model_deletePoint_not_ok2(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 5
        response = ['0#']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deletePoint(1)
            self.assertEqual(False, suc)

    def test_Model_deletePoint_not_ok3(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 5
        response = ['0#']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deletePoint(1)
            self.assertEqual(False, suc)

    def test_Model_deletePoint_not_ok4(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 5
        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deletePoint(10)
            self.assertEqual(False, suc)

    def test_Model_deletePoint_not_ok5(self):
        model = Model(host=None, parent=Parent())
        model.numberStars = 5
        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deletePoint('e')
            self.assertEqual(False, suc)

    #
    #
    # testing storeName
    #
    #

    def test_Model_storeName_ok1(self):
        model = Model(host=None, parent=Parent())

        response = ['1', '1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = model.storeName('test')
            self.assertEqual(True, suc)

    def test_Model_storeName_ok2(self):
        model = Model(host=None, parent=Parent())

        response = ['0', '1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = model.storeName('Test')
            self.assertEqual(True, suc)

    def test_Model_storeName_not_ok1(self):
        model = Model(host=None, parent=Parent())

        response = ['1', '0']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = model.storeName('test')
            self.assertEqual(False, suc)

    def test_Model_storeName_not_ok2(self):
        model = Model(host=None, parent=Parent())

        response = ['1', '1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 2
            suc = model.storeName('test')
            self.assertEqual(False, suc)

    def test_Model_storeName_not_ok3(self):
        model = Model(host=None, parent=Parent())

        response = ['1', '1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = model.storeName('1234567890123456')
            self.assertEqual(False, suc)

    def test_Model_storeName_not_ok4(self):
        model = Model(host=None, parent=Parent())

        response = ['0', '1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = model.storeName(2423487)
            self.assertEqual(False, suc)

    #
    #
    # testing loadName
    #
    #

    def test_Model_loadName_ok(self):
        model = Model(host=None, parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.loadName('test')
            self.assertEqual(True, suc)

    def test_Model_loadName_not_ok1(self):
        model = Model(host=None, parent=Parent())

        response = ['0']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.loadName('test')
            self.assertEqual(False, suc)

    def test_Model_loadName_not_ok2(self):
        model = Model(host=None, parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = model.loadName('test')
            self.assertEqual(False, suc)

    def test_Model_loadName_not_ok3(self):
        model = Model(host=None, parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.loadName('1234567890123456')
            self.assertEqual(False, suc)

    def test_Model_loadName_not_ok4(self):
        model = Model(host=None, parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.loadName(3567)
            self.assertEqual(False, suc)

    #
    #
    # testing deleteName
    #
    #

    def test_Model_deleteName_ok(self):
        model = Model(host=None, parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deleteName('test')
            self.assertEqual(True, suc)

    def test_Model_deleteName_not_ok1(self):
        model = Model(host=None, parent=Parent())

        response = ['0']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deleteName('test')
            self.assertEqual(False, suc)

    def test_Model_deleteName_not_ok2(self):
        model = Model(host=None, parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = model.deleteName('test')
            self.assertEqual(False, suc)

    def test_Model_deleteName_not_ok3(self):
        model = Model(host=None, parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deleteName('1234567890123456')
            self.assertEqual(False, suc)

    def test_Model_deleteName_not_ok4(self):
        model = Model(host=None, parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = model.deleteName(3567)
            self.assertEqual(False, suc)

    #
    #
    # testing programAlign
    #
    #

    def test_Model_programAlign_ok1(self):
        model = Model(host=None, parent=Parent())

        aPoint = AlignStar()
        build = [aPoint]
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['1'], 1
            suc = model.programAlign(build)
            self.assertEqual(True, suc)

    def test_Model_programAlign_ok2(self):
        model = Model(host=None, parent=Parent())

        aPoint = AlignStar()
        build = [aPoint]
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['1'], 1
            suc = model.programAlign(build)
            self.assertEqual(True, suc)
            mConn.return_value.communicate.assert_called_with(':newalig#:endalig#')

    def test_Model_programAlign_ok3(self):
        model = Model(host=None, parent=Parent())
        v1 = ':newalig#:newalpt19:35:15.6,-15*02:43.1,W,19:35:45.3,-15*03:41.8,' \
             '17:35:31.75#:endalig#'

        build = self.gatherData(1)
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['E'], 1
            suc = model.programAlign(build)
            self.assertEqual(False, suc)
            mConn.return_value.communicate.assert_called_with(v1)

    def test_Model_programAlign_not_ok0(self):
        model = Model(host=None, parent=Parent())
        v1 = ':newalig#:newalpt19:35:15.6,-15*02:43.1,W,19:35:45.3,-15*03:41.8,' \
             '17:35:31.75#:endalig#'

        build = self.gatherData(2)
        build[1].mCoord = None
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['E'], 1
            suc = model.programAlign(build)
            self.assertEqual(False, suc)
            mConn.return_value.communicate.assert_called_with(v1)

    def test_Model_programAlign_not_ok1(self):
        model = Model(host=None, parent=Parent())

        aPoint = AlignStar()
        build = [aPoint]
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['E'], 1
            suc = model.programAlign(build)
            self.assertEqual(False, suc)

    def test_Model_programAlign_not_ok2(self):
        model = Model(host=None, parent=Parent())

        aPoint = AlignStar()
        build = [aPoint, 'test']
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['E'], 1
            suc = model.programAlign(build)
            self.assertEqual(False, suc)

    def test_Model_programAlign_not_ok3(self):
        model = Model(host=None, parent=Parent())

        aPoint = AlignStar()
        build = [aPoint]
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['E'], 1
            suc = model.programAlign(build)
            self.assertEqual(False, suc)

    def test_Model_programAlign_not_ok4(self):
        model = Model(host=None, parent=Parent())

        build = 'Test'
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['E'], 1
            suc = model.programAlign(build)
            self.assertEqual(False, suc)

    def test_Model_programAlign_not_ok5(self):
        model = Model(host=None, parent=Parent())

        aPoint = AlignStar()
        build = [aPoint]
        with mock.patch('mountcontrol.model.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, ['1'], 1
            suc = model.programAlign(build)
            self.assertEqual(False, suc)
            mConn.return_value.communicate.assert_called_with(':newalig#:endalig#')

    @staticmethod
    def gatherData(number):
        filename = 'tests/testData/2018-07-08-21-41-44_full.dat'
        import json
        with open(filename, 'r') as infile:
            data = json.load(infile)

        maxNum = len(data['Index'])
        if number > maxNum:
            number = maxNum
        build = []
        for i in range(0, number):
            aPoint = AlignStar()
            aPoint.mCoord = skyfield.api.Star(ra_hours=data['RaJNow'][i],
                                              dec_degrees=data['DecJNow'][i])
            aPoint.sCoord = skyfield.api.Star(ra_hours=data['RaJNowSolved'][i],
                                              dec_degrees=data['DecJNowSolved'][i])
            aPoint.pierside = data['Pierside'][i]
            aPoint.sidereal = data['LocalSiderealTime'][i]
            build.append(aPoint)
        build.append(AlignStar())
        return build
