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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import os
import json
import binascii
import unittest.mock as mock
import faulthandler
faulthandler.enable()

# external packages
import skyfield.api
from skyfield.toposlib import Topos
from mountcontrol.mount import Mount

# local import
from mw4.modeldata.buildpoints import DataPoint
from mw4.modeldata.buildpoints import HaDecToAltAz


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test():
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

    global app
    config = 'mw4/test/config'
    testdir = os.listdir(config)
    for item in testdir:
        if item.endswith('.bpts'):
            os.remove(os.path.join(config, item))
        if item.endswith('.hpts'):
            os.remove(os.path.join(config, item))

    app = DataPoint(app=Test(),
                     configDir='mw4/test/config',
                     )
    yield


def test_topoToAltAz1():
    ha = 12
    dec = 0
    alt, az = HaDecToAltAz(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_topoToAltAz2():
    ha = -12
    dec = 0
    alt, az = HaDecToAltAz(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_genHaDecParams1():
    selection = 'min'
    length = len(app.DEC[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC[selection][j]
        assert b == app.STEP[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_genHaDecParams2():
    selection = 'norm'
    length = len(app.DEC[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC[selection][j]
        assert b == app.STEP[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_genHaDecParams3():
    selection = 'med'
    length = len(app.DEC[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC[selection][j]
        assert b == app.STEP[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_genHaDecParams4():
    selection = 'max'
    length = len(app.DEC[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC[selection][j]
        assert b == app.STEP[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_genHaDecParams5():
    selection = 'test'
    val = True
    for i, (_, _, _, _) in enumerate(app.genHaDecParams(selection=selection)):
        val = False
    assert val


def test_isCloseMeridian_1():
    suc = app.isCloseMeridian((90, 45))
    assert suc


def test_isCloseMeridian_2():
    app.app.mount.setting.meridianLimitSlew = 5
    app.app.mount.setting.meridianLimitTrack = 5
    suc = app.isCloseMeridian((90, 45))
    assert suc


def test_deleteCloseMeridian_1():
    suc = app.deleteCloseMeridian()
    assert suc


def test_genGreaterCircle1():
    app.lat = 48
    selection = 'min'
    app.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(app.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 50


def test_genGreaterCircle2():
    app.lat = 48
    selection = 'norm'
    app.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(app.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 75


def test_genGreaterCircle3():
    app.lat = 48
    selection = 'med'
    app.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(app.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 94


def test_genGreaterCircle4():
    app.lat = 48
    selection = 'max'
    app.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(app.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 124


def test_checkFormat_1():
    a = [[1, 1], [1, 1]]
    suc = app.checkFormat(a)
    assert suc


def test_checkFormat_2():
    a = [[1, 1], [1]]
    suc = app.checkFormat(a)
    assert not suc


def test_checkFormat_3():
    a = [[1, 1], (1, 1)]
    suc = app.checkFormat(a)
    assert not suc


def test_checkFormat_4():
    a = 'test'
    suc = app.checkFormat(a)
    assert not suc


def test_buildP1():
    app.buildP = ()
    app.genGreaterCircle('max')
    assert len(app.buildP) == 125
    app.genGreaterCircle('med')
    assert len(app.buildP) == 95
    app.genGreaterCircle('norm')
    assert len(app.buildP) == 76
    app.genGreaterCircle('min')
    assert len(app.buildP) == 51


def test_buildP2():
    app.buildP = ()
    app.buildP = '456'
    assert len(app.buildP) == 0


def test_buildP3():
    app.buildP = ()
    app.buildP = [(1, 1), (1, 1), 'test']
    assert len(app.buildP) == 0


def test_clearBuildP():
    app.buildP = ()
    app.genGreaterCircle('max')
    assert len(app.buildP) == 125
    app.clearBuildP()
    assert len(app.buildP) == 0


def test_addBuildP1():
    app.buildP = ()
    suc = app.addBuildP((10, 10))
    assert suc
    assert 1 == len(app.buildP)
    suc = app.addBuildP((10, 10))
    assert suc
    assert 2 == len(app.buildP)
    suc = app.addBuildP((10, 10))
    assert suc
    assert 3 == len(app.buildP)


def test_addBuildP2():
    app.buildP = ()
    suc = app.addBuildP(10)
    assert not suc
    assert 0 == len(app.buildP)


def test_addBuildP3():
    app.buildP = ()
    suc = app.addBuildP((10, 10, 10))
    assert not suc
    assert 0 == len(app.buildP)


def test_addBuildP4():
    app.buildP = [(10, 10), (10, 10)]
    suc = app.addBuildP((10, 10), position=1)
    assert suc
    assert len(app.buildP) == 3


def test_addBuildP5():
    app.buildP = [(10, 10), (10, 10)]
    suc = app.addBuildP((10, 10), position=20)
    assert suc
    assert len(app.buildP) == 3


def test_addBuildP6():
    app.buildP = [(10, 10), (10, 10)]
    suc = app.addBuildP((10, 10), position=-5)
    assert suc
    assert len(app.buildP) == 3


def test_addBuildP7():
    app.buildP = [(10, 10), (10, 10)]
    suc = app.addBuildP(position=-5)
    assert not suc


def test_delBuildP1():
    app.buildP = ()
    app.genGreaterCircle('max')
    assert len(app.buildP) == 125
    suc = app.delBuildP(5)
    assert suc
    assert len(app.buildP) == 124
    suc = app.delBuildP(0)
    assert suc
    assert len(app.buildP) == 123
    suc = app.delBuildP(121)
    assert suc
    assert len(app.buildP) == 122


def test_delBuildP2():
    app.buildP = ()
    app.genGreaterCircle('max')
    assert len(app.buildP) == 125
    suc = app.delBuildP(-5)
    assert not suc
    assert len(app.buildP) == 125


def test_delBuildP3():
    app.buildP = ()
    app.genGreaterCircle('max')
    assert len(app.buildP) == 125
    suc = app.delBuildP(170)
    assert not suc
    assert len(app.buildP) == 125


def test_delBuildP4():
    app.buildP = ()
    app.genGreaterCircle('max')
    assert len(app.buildP) == 125
    suc = app.delBuildP('1')
    assert not suc
    assert len(app.buildP) == 125


def test_horizonP1():
    app.clearHorizonP()
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 127
    app.genGreaterCircle('med')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 97
    app.genGreaterCircle('norm')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 78
    app.genGreaterCircle('min')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 53


def test_horizonP2():
    app.horizonP = ()
    app.horizonP = '456'
    assert len(app.horizonP) == 2


def test_horizonP3():
    app.horizonP = ()
    app.horizonP = [(1, 1), (1, 1), 'test']
    assert len(app.horizonP) == 2


def test_clearHorizonP():
    app.horizonP = ()
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 127
    app.clearHorizonP()
    assert len(app.horizonP) == 2


def test_addHorizonP1():
    app.horizonP = ()
    suc = app.addHorizonP((10, 10))
    assert suc
    assert len(app.horizonP) == 3
    suc = app.addHorizonP((10, 10))
    assert suc
    assert len(app.horizonP) == 4
    suc = app.addHorizonP((10, 10))
    assert suc
    assert len(app.horizonP) == 5


def test_addHorizonP2():
    app.horizonP = ()
    suc = app.addHorizonP(10)
    assert not suc
    assert len(app.horizonP) == 2


def test_addHorizonP3():
    app.horizonP = ()
    suc = app.addHorizonP((10, 10, 10))
    assert not suc
    assert len(app.horizonP) == 2


def test_addHorizonP4():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP((10, 10), position=1)
    assert suc
    assert len(app.horizonP) == 5


def test_addHorizonP5():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP((10, 10), position=20)
    assert suc
    assert len(app.horizonP) == 5


def test_addHorizonP6():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP((10, 10), position=-5)
    assert suc
    assert len(app.horizonP) == 5


def test_addHorizonP7():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP(position=-5)
    assert not suc


def test_delHorizonP1():
    app.horizonP = ()
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 127
    suc = app.delHorizonP(5)
    assert suc
    assert len(app.horizonP) == 126
    suc = app.delHorizonP(1)
    assert suc
    assert len(app.horizonP) == 125
    suc = app.delHorizonP(10)
    assert suc
    assert len(app.horizonP) == 124


def test_delHorizonP2():
    app.horizonP = ()
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 127
    suc = app.delHorizonP(-5)
    assert not suc
    assert len(app.horizonP) == len(app.buildP)


def test_delHorizonP3():
    app.horizonP = ()
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == len(app.buildP)
    suc = app.delHorizonP(170)
    assert not suc
    assert len(app.horizonP) == len(app.buildP)


def test_delHorizonP4():
    app.horizonP = ()
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == len(app.buildP)
    suc = app.delHorizonP('1')
    assert not suc
    assert len(app.horizonP) == len(app.buildP)


def test_delHorizonP5():
    app.horizonP = [(1, 1), (3, 3), (10, 10)]
    suc = app.delHorizonP(position=0)
    assert not suc
    suc = app.delHorizonP(154)
    assert not suc


def test_saveBuildP_11():
    app.genGreaterCircle('min')
    suc = app.saveBuildP()
    assert not suc


def test_saveBuildP_12():
    fileName = 'mw4/test/config/save_test.bpts'
    app.genGreaterCircle('min')
    suc = app.saveBuildP('save_test')
    assert suc
    assert os.path.isfile(fileName)


def test_loadBuildP_11():
    # wrong fileName given
    suc = app.loadBuildP()
    assert not suc


def test_loadBuildP_12():
    # path with not existent file given
    suc = app.loadBuildP(fileName='test_file_not_there')
    assert not suc


def test_loadBuildP_13():
    # load file with path
    app.buildPFile = ''
    fileName = 'mw4/test/config/test.bpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = app.loadBuildP(fileName='test')
    assert suc
    assert app.buildP == values


def test_loadBuildP_14():
    # load with wrong content
    app.buildPFile = ''
    fileName = 'mw4/test/config/test.bpts'
    with open(fileName, 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))
    suc = app.loadBuildP(fileName='test')
    assert not suc
    assert app.buildP == []


def test_loadBuildP_15():
    # load with wrong content 2
    app.buildPFile = ''
    fileName = 'mw4/test/config/test.bpts'
    with open(fileName, 'w') as outfile:
        outfile.writelines('[test, ]],[]}')
    suc = app.loadBuildP(fileName='test')
    assert not suc
    assert app.buildP == []


def test_loadBuildP_16():
    # load file without path
    fileName = 'mw4/test/config/test.bpts'
    app.buildPFile = 'test'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    with mock.patch.object(app,
                           'checkFormat',
                           return_value=False):
        suc = app.loadBuildP()
        assert not suc


def test_checkBoundaries_1():
    points = [(0, 0), (0, 1), (0, 2), (0, 360)]
    pointsRet = [(0, 1), (0, 2)]
    value = app.checkBoundaries(points)
    assert pointsRet == value


def test_checkBoundaries_2():
    points = [(0, 1), (0, 2), (0, 360)]
    pointsRet = [(0, 1), (0, 2)]
    value = app.checkBoundaries(points)
    assert pointsRet == value


def test_checkBoundaries_3():
    points = [(0, 0), (0, 1), (0, 2)]
    pointsRet = [(0, 1), (0, 2)]
    value = app.checkBoundaries(points)
    assert pointsRet == value


def test_saveHorizonP_10():
    app._horizonP = [(0, 1), (0, 2)]
    suc = app.saveHorizonP(fileName='test_save_horizon')
    assert suc


def test_saveHorizonP_11():
    app._horizonP = [(0, 1), (0, 2)]
    suc = app.saveHorizonP()
    assert not suc


def test_saveHorizonP_12():
    app._horizonP = [(0, 0), (0, 1), (0, 2), (0, 360)]
    suc = app.saveHorizonP(fileName='test_horizon_1')
    assert suc
    fileName = 'mw4/test/config/' + 'test_horizon_1' + '.hpts'
    with open(fileName, 'r') as infile:
        value = json.load(infile)
        assert value[0] != [0, 0]
        assert value[-1] != [0, 360]


def test_loadHorizonP_10():
    # no fileName given
    suc = app.loadHorizonP()
    assert not suc


def test_loadHorizonP_11():
    # wrong fileName given
    suc = app.loadHorizonP(fileName='format_not_ok')
    assert not suc


def test_loadHorizonP_12():
    # path with not existent file given
    fileName = 'mw4/test/config/test_load_horizon.hpts'
    suc = app.loadHorizonP(fileName=fileName)
    assert not suc


def test_loadHorizonP_13():
    # load file with path
    fileName = 'mw4/test/config/test_horizon_2.hpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = app.loadHorizonP(fileName='test_horizon_2')
    assert suc
    assert app.horizonP == [(0, 0)] + values + [(0, 360)]


def test_loadHorizonP_14():
    # load with wrong content
    app.horizonPFile = ''
    fileName = 'mw4/test/config/test_horizon_2.hpts'
    with open(fileName, 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))
    suc = app.loadHorizonP(fileName='test_horizon_2')
    assert not suc
    assert app.horizonP == [(0, 0), (0, 360)]


def test_loadHorizonP_15():
    # load with wrong content 2
    app.horizonPFile = ''
    fileName = 'mw4/test/config/test_horizon_2.hpts'
    with open(fileName, 'w') as outfile:
        outfile.writelines('[test, ]],[]}')
    suc = app.loadHorizonP(fileName='test_horizon_2')
    assert not suc
    assert app.horizonP == [(0, 0), (0, 360)]


def test_genGrid1():
    suc = app.genGrid(minAlt=10,
                      maxAlt=80,
                      numbRows=4,
                      numbCols=4)
    assert suc


def test_genGrid2():
    suc = app.genGrid(minAlt=0,
                      maxAlt=80,
                      numbRows=4,
                      numbCols=4)
    assert not suc


def test_genGrid3():
    suc = app.genGrid(minAlt=10,
                      maxAlt=90,
                      numbRows=4,
                      numbCols=4)
    assert not suc


def test_genGrid4():
    suc = app.genGrid(minAlt=50,
                      maxAlt=40,
                      numbRows=4,
                      numbCols=3)
    assert not suc


def test_genGrid5():
    suc = app.genGrid(minAlt=10,
                      maxAlt=40,
                      numbRows=4,
                      numbCols=4)
    assert suc


def test_genGrid6():
    suc = app.genGrid(minAlt=10,
                      maxAlt=90,
                      numbRows=4,
                      numbCols=3)
    assert not suc


def test_genGrid7():
    suc = app.genGrid(minAlt=10,
                      maxAlt=80,
                      numbRows=4,
                      numbCols=3)
    assert not suc


def test_genGridData1():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=4,
                numbCols=4)
    assert 16 == len(app.buildP)


def test_genGridData2():
    app.genGrid(minAlt=5,
                maxAlt=85,
                numbRows=4,
                numbCols=4)
    assert 16 == len(app.buildP)


def test_genGridData3():
    app.genGrid(minAlt=5,
                maxAlt=85,
                numbRows=8,
                numbCols=8)
    assert 64 == len(app.buildP)


def test_genGridData4():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=6,
                numbCols=6)
    assert 36 == len(app.buildP)


def test_genGridData5():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=6,
                numbCols=12)
    assert 72 == len(app.buildP)


def test_genGridData6():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=1,
                numbCols=12)
    assert 0 == len(app.buildP)


def test_genGridData7():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=5,
                numbCols=1)
    assert 0 == len(app.buildP)


def test_genGridData8():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=10,
                numbCols=12)
    assert 0 == len(app.buildP)


def test_genGridData9():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=6,
                numbCols=20)
    assert 0 == len(app.buildP)


def test_genAlign1():
    suc = app.genAlign(altBase=30,
                       azBase=30,
                       numberBase=5,
                       )
    assert suc
    assert 5 == len(app.buildP)


def test_genAlign2():
    suc = app.genAlign(altBase=0,
                       azBase=30,
                       numberBase=5,
                       )
    assert not suc
    assert 0 == len(app.buildP)


def test_genAlign3():
    suc = app.genAlign(altBase=30,
                       azBase=-10,
                       numberBase=5,
                       )
    assert not suc
    assert 0 == len(app.buildP)


def test_genAlign4():
    suc = app.genAlign(altBase=30,
                       azBase=30,
                       numberBase=2,
                       )
    assert not suc
    assert 0 == len(app.buildP)


def test_genAlign5():
    suc = app.genAlign(altBase=30,
                       azBase=30,
                       numberBase=30,
                       )
    assert not suc
    assert 0 == len(app.buildP)


def test_isAboveHorizon():
    app.clearHorizonP()
    suc = app.isAboveHorizon((10, 50))
    assert suc
    suc = app.isAboveHorizon((10, 370))
    assert suc
    suc = app.isAboveHorizon((10, -50))
    assert suc
    suc = app.isAboveHorizon((-10, 50))
    assert not suc


def test_deleteBelowHorizon1():
    app.clearHorizonP()
    app.buildP = [(10, 10), (-5, 40), (40, 60)]
    app.deleteBelowHorizon()
    assert len(app.buildP) == 2


def test_deleteBelowHorizon2():
    app.clearHorizonP()
    app.buildP = [(10, 10), (5, 40), (-40, 60)]
    app.deleteBelowHorizon()
    assert len(app.buildP) == 2


def test_deleteBelowHorizon3():
    app.clearHorizonP()
    app.buildP = [(-10, 10), (5, 40), (40, 60)]
    app.deleteBelowHorizon()
    assert len(app.buildP) == 2


def test_deleteBelowHorizon4():
    app.clearHorizonP()
    app.buildP = [(-10, 10), (-5, 40), (-40, 60)]
    app.deleteBelowHorizon()
    assert len(app.buildP) == 0


def test_sort_1():
    values = [(10, 10), (20, 20), (30, 90), (40, 190), (50, 290)]
    app._buildP = values
    suc = app.sort()
    assert not suc
    assert app.buildP == values


def test_sort_2():
    values = [(10, 10), (20, 20), (30, 90), (40, 190), (50, 290)]
    app._buildP = values
    suc = app.sort(eastwest=True, highlow=True)
    assert not suc
    assert app.buildP == values


def test_sort_3():
    values = [(10, 10), (20, 20), (30, 90), (40, 190), (50, 290)]
    result = [(30, 90), (20, 20), (10, 10), (50, 290), (40, 190)]
    app._buildP = values
    suc = app.sort(eastwest=True, highlow=False)
    assert suc
    assert app.buildP == result


def test_sort_4():
    values = [(10, 10), (20, 20), (30, 90), (40, 190), (50, 290)]
    result = [(30, 90), (20, 20), (10, 10), (50, 290), (40, 190)]
    app._buildP = values
    suc = app.sort(eastwest=False, highlow=True)
    assert suc
    assert app.buildP == result


def test_sort_5():
    values = [(30, 90), (50, 290), (20, 20), (10, 10), (40, 190)]
    result = [(30, 90), (20, 20), (10, 10), (50, 290), (40, 190)]
    app._buildP = values
    suc = app.sort(eastwest=True, highlow=False)
    assert suc
    assert app.buildP == result


def test_sort_6():
    values = [(30, 90), (50, 290), (20, 20), (10, 10), (40, 190)]
    result = [(30, 90), (20, 20), (10, 10), (50, 290), (40, 190)]
    app._buildP = values
    suc = app.sort(eastwest=False, highlow=True)
    assert suc
    assert app.buildP == result


def test_generateCelestialEquator():
    value = app.generateCelestialEquator()
    assert len(value) == 3000


def test_generateDSOPath_1():
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    suc = app.generateDSOPath(ra=ra,
                              dec=dec,
                              numberPoints=0,
                              duration=1,
                              timeShift=0,
                              )
    assert not suc


def test_generateDSOPath_2():
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    suc = app.generateDSOPath(ra=ra,
                              dec=dec,
                              numberPoints=1,
                              duration=0,
                              timeShift=0,
                              )
    assert not suc


def test_generateDSOPath_3():
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    suc = app.generateDSOPath(ra=ra,
                              dec=dec,
                              numberPoints=1,
                              duration=1,
                              timeShift=0,
                              timeJD=app.app.mount.obsSite.timeJD,
                              location=app.app.mount.obsSite.location,
                              )
    assert suc


def test_generateGoldenSpiral_1():
    suc = app.generateGoldenSpiral(0)
    assert not suc


def test_generateGoldenSpiral_2():
    suc = app.generateGoldenSpiral(200)
    assert suc
