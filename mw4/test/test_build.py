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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import os
import json
import binascii
# external packages
# local import

from mw4.build import build

mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'build': 'test',
          }


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global data
    config = mwGlob['configDir']
    testdir = os.listdir(config)
    for item in testdir:
        if item.endswith('.bpts'):
            os.remove(os.path.join(config, item))
        if item.endswith('.hpts'):
            os.remove(os.path.join(config, item))
    data = build.DataPoint(mwGlob=mwGlob, lat=48)
    yield
    data = None


def test_topoToAzAlt1():
    ha = 12
    dec = 0
    alt, az = data.topoToAzAlt(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_topoToAzAlt2():
    ha = -12
    dec = 0
    alt, az = data.topoToAzAlt(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_genHaDecParams1():
    selection = 'min'
    length = len(data.DEC[selection])
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == data.DEC[selection][j]
        assert b == data.STEP[selection][j]
        assert c == data.START[selection][i]
        assert d == data.STOP[selection][i]


def test_genHaDecParams2():
    selection = 'norm'
    length = len(data.DEC[selection])
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == data.DEC[selection][j]
        assert b == data.STEP[selection][j]
        assert c == data.START[selection][i]
        assert d == data.STOP[selection][i]


def test_genHaDecParams3():
    selection = 'med'
    length = len(data.DEC[selection])
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == data.DEC[selection][j]
        assert b == data.STEP[selection][j]
        assert c == data.START[selection][i]
        assert d == data.STOP[selection][i]


def test_genHaDecParams4():
    selection = 'max'
    length = len(data.DEC[selection])
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == data.DEC[selection][j]
        assert b == data.STEP[selection][j]
        assert c == data.START[selection][i]
        assert d == data.STOP[selection][i]


def test_genHaDecParams5():
    selection = 'test'
    val = True
    for i, (_, _, _, _) in enumerate(data.genHaDecParams(selection=selection)):
        val = False
    assert val


def test_genGreaterCircle1():
    data.lat = 48
    selection = 'min'
    data.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(data.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 58


def test_genGreaterCircle2():
    data.lat = 48
    selection = 'norm'
    data.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(data.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 89 == i


def test_genGreaterCircle3():
    data.lat = 48
    selection = 'med'
    data.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(data.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 109 == i


def test_genGreaterCircle4():
    data.lat = 48
    selection = 'max'
    data.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(data.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 152 == i


def test_checkFormat_1():
    a = [[1, 1], [1, 1]]
    suc = data.checkFormat(a)
    assert suc


def test_checkFormat_2():
    a = [[1, 1], [1]]
    suc = data.checkFormat(a)
    assert not suc


def test_checkFormat_3():
    a = [[1, 1], (1, 1)]
    suc = data.checkFormat(a)
    assert not suc


def test_buildP1():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 153
    data.genGreaterCircle('med')
    assert len(data.buildP) == 110
    data.genGreaterCircle('norm')
    assert len(data.buildP) == 90
    data.genGreaterCircle('min')
    assert len(data.buildP) == 59


def test_buildP2():
    data.buildP = ()
    data.buildP = '456'
    assert len(data.buildP) == 0


def test_buildP3():
    data.buildP = ()
    data.buildP = [(1, 1), (1, 1), 'test']
    assert len(data.buildP) == 0


def test_clearBuildP():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 153
    data.clearBuildP()
    assert len(data.buildP) == 0


def test_addBuildP1():
    data.buildP = ()
    suc = data.addBuildP((10, 10))
    assert suc
    assert 1 == len(data.buildP)
    suc = data.addBuildP((10, 10))
    assert suc
    assert 2 == len(data.buildP)
    suc = data.addBuildP((10, 10))
    assert suc
    assert 3 == len(data.buildP)


def test_addBuildP2():
    data.buildP = ()
    suc = data.addBuildP(10)
    assert not suc
    assert 0 == len(data.buildP)


def test_addBuildP3():
    data.buildP = ()
    suc = data.addBuildP((10, 10, 10))
    assert not suc
    assert 0 == len(data.buildP)


def test_addBuildP4():
    data.buildP = [(10, 10), (10, 10)]
    suc = data.addBuildP((10, 10), position=1)
    assert suc
    assert len(data.buildP) == 3


def test_addBuildP5():
    data.buildP = [(10, 10), (10, 10)]
    suc = data.addBuildP((10, 10), position=20)
    assert suc
    assert len(data.buildP) == 3


def test_addBuildP6():
    data.buildP = [(10, 10), (10, 10)]
    suc = data.addBuildP((10, 10), position=-5)
    assert suc
    assert len(data.buildP) == 3


def test_delBuildP1():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 153
    suc = data.delBuildP(5)
    assert suc
    assert len(data.buildP) == 152
    suc = data.delBuildP(0)
    assert suc
    assert len(data.buildP) == 151
    suc = data.delBuildP(150)
    assert suc
    assert len(data.buildP) == 150


def test_delBuildP2():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 153
    suc = data.delBuildP(-5)
    assert not suc
    assert len(data.buildP) == 153


def test_delBuildP3():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 153
    suc = data.delBuildP(170)
    assert not suc
    assert len(data.buildP) == 153


def test_delBuildP4():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 153
    suc = data.delBuildP('1')
    assert not suc
    assert len(data.buildP) == 153


def test_horizonP1():
    data.clearHorizonP()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 155
    data.genGreaterCircle('med')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 56
    data.genGreaterCircle('norm')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 37
    data.genGreaterCircle('min')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 14


def test_horizonP2():
    data.horizonP = ()
    data.horizonP = '456'
    assert len(data.horizonP) == 2


def test_horizonP3():
    data.horizonP = ()
    data.horizonP = [(1, 1), (1, 1), 'test']
    assert len(data.horizonP) == 2


def test_clearHorizonP():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 155
    data.clearHorizonP()
    assert len(data.horizonP) == 2


def test_addHorizonP1():
    data.horizonP = ()
    suc = data.addHorizonP((10, 10))
    assert suc
    assert len(data.horizonP) == 3
    suc = data.addHorizonP((10, 10))
    assert suc
    assert len(data.horizonP) == 4
    suc = data.addHorizonP((10, 10))
    assert suc
    assert len(data.horizonP) == 5


def test_addHorizonP2():
    data.horizonP = ()
    suc = data.addHorizonP(10)
    assert not suc
    assert len(data.horizonP) == 2


def test_addHorizonP3():
    data.horizonP = ()
    suc = data.addHorizonP((10, 10, 10))
    assert not suc
    assert len(data.horizonP) == 2


def test_addHorizonP4():
    data.horizonP = [(10, 10), (10, 10)]
    suc = data.addHorizonP((10, 10), position=1)
    assert suc
    assert len(data.horizonP) == 5


def test_addHorizonP5():
    data.horizonP = [(10, 10), (10, 10)]
    suc = data.addHorizonP((10, 10), position=20)
    assert suc
    assert len(data.horizonP) == 5


def test_addHorizonP6():
    data.horizonP = [(10, 10), (10, 10)]
    suc = data.addHorizonP((10, 10), position=-5)
    assert suc
    assert len(data.horizonP) == 5


def test_delHorizonP1():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 155
    suc = data.delHorizonP(5)
    assert suc
    assert len(data.horizonP) == 154
    suc = data.delHorizonP(1)
    assert suc
    assert len(data.horizonP) == 153
    suc = data.delHorizonP(150)
    assert suc
    assert len(data.horizonP) == 152


def test_delHorizonP2():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 155
    suc = data.delHorizonP(-5)
    assert not suc
    assert len(data.horizonP) == 155


def test_delHorizonP3():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 155
    suc = data.delHorizonP(170)
    assert not suc
    assert len(data.horizonP) == 155


def test_delHorizonP4():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 155
    suc = data.delHorizonP('1')
    assert not suc
    assert len(data.horizonP) == 155


def test_saveBuildP():
    data.buildPFile = 'test'
    data.genGreaterCircle('min')
    suc = data.saveBuildP()
    assert suc


def test_loadBuildP_10():
    # no fileName given
    data.buildPFile = ''
    suc = data.loadBuildP()
    assert not suc


def test_loadBuildP_11():
    # wrong fileName given
    data.buildPFile = 'format_not_ok'
    suc = data.loadBuildP()
    assert not suc


def test_loadBuildP_12():
    # path with not existent file given
    fileName = mwGlob['configDir'] + '/test.bpts'
    suc = data.loadBuildP(fileName=fileName)
    assert not suc


def test_loadBuildP_13():
    # load file without path
    fileName = mwGlob['configDir'] + '/test.bpts'
    data.buildPFile = 'test'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = data.loadBuildP()
    assert suc
    assert data.buildPFile == 'test'
    assert data.buildP == values


def test_loadBuildP_14():
    # load file with path
    data.buildPFile = ''
    fileName = mwGlob['configDir'] + '/test.bpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = data.loadBuildP(fileName=fileName)
    assert suc
    assert data.buildPFile == 'test'
    assert data.buildP == values


def test_loadBuildP_15():
    # load with wrong content
    data.buildPFile = ''
    fileName = mwGlob['configDir'] + '/test.bpts'
    with open(fileName, 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))
    suc = data.loadBuildP(fileName=fileName)
    assert not suc
    assert data.buildP == []


def test_loadBuildP_16():
    # load with wrong content 2
    data.buildPFile = ''
    fileName = mwGlob['configDir'] + '/test.bpts'
    with open(fileName, 'w') as outfile:
        outfile.writelines('[test, ]],[]}')
    suc = data.loadBuildP(fileName=fileName)
    assert not suc
    assert data.buildP == []


def test_saveHorizonP1():
    data.horizonPFile = 'test'
    data.genGreaterCircle('min')
    suc = data.saveHorizonP()
    assert suc


def test_loadHorizonP_10():
    # no fileName given
    data.horizonPFile = ''
    suc = data.loadHorizonP()
    assert not suc


def test_loadHorizonP_11():
    # wrong fileName given
    data.horizonPFile = 'format_not_ok'
    suc = data.loadHorizonP()
    assert not suc


def test_loadHorizonP_12():
    # path with not existent file given
    fileName = mwGlob['configDir'] + '/test.hpts'
    suc = data.loadHorizonP(fileName=fileName)
    assert not suc


def test_loadHorizonP_13():
    # load file without path
    fileName = mwGlob['configDir'] + '/test.hpts'
    data.horizonPFile = 'test'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = data.loadHorizonP()
    assert suc
    assert data.horizonPFile == 'test'
    assert data.horizonP == [(0, 0)] + values + [(0, 360)]


def test_loadHorizonP_14():
    # load file with path
    data.horizonPFile = ''
    fileName = mwGlob['configDir'] + '/test.hpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = data.loadHorizonP(fileName=fileName)
    assert suc
    assert data.horizonPFile == 'test'
    assert data.horizonP == [(0, 0)] + values + [(0, 360)]


def test_loadHorizonP_15():
    # load with wrong content
    data.horizonPFile = ''
    fileName = mwGlob['configDir'] + '/test.hpts'
    with open(fileName, 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))
    suc = data.loadHorizonP(fileName=fileName)
    assert not suc
    assert data.horizonP == [(0, 0), (0, 360)]


def test_loadHorizonP_16():
    # load with wrong content 2
    data.horizonPFile = ''
    fileName = mwGlob['configDir'] + '/test.hpts'
    with open(fileName, 'w') as outfile:
        outfile.writelines('[test, ]],[]}')
    suc = data.loadHorizonP(fileName=fileName)
    assert not suc
    assert data.horizonP == [(0, 0), (0, 360)]


def test_genGrid1():
    suc = data.genGrid(minAlt=10,
                       maxAlt=80,
                       numbRows=4,
                       numbCols=4)
    assert suc


def test_genGrid2():
    suc = data.genGrid(minAlt=0,
                       maxAlt=80,
                       numbRows=4,
                       numbCols=4)
    assert not suc


def test_genGrid3():
    suc = data.genGrid(minAlt=10,
                       maxAlt=90,
                       numbRows=4,
                       numbCols=4)
    assert not suc


def test_genGrid4():
    suc = data.genGrid(minAlt=50,
                       maxAlt=40,
                       numbRows=4,
                       numbCols=3)
    assert not suc


def test_genGrid5():
    suc = data.genGrid(minAlt=10,
                       maxAlt=40,
                       numbRows=4,
                       numbCols=4)
    assert suc


def test_genGrid6():
    suc = data.genGrid(minAlt=10,
                       maxAlt=90,
                       numbRows=4,
                       numbCols=3)
    assert not suc


def test_genGridData1():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=4,
                 numbCols=4)
    assert 16 == len(data.buildP)


def test_genGridData2():
    data.genGrid(minAlt=5,
                 maxAlt=85,
                 numbRows=4,
                 numbCols=4)
    assert 16 == len(data.buildP)


def test_genGridData3():
    data.genGrid(minAlt=5,
                 maxAlt=85,
                 numbRows=8,
                 numbCols=8)
    assert 64 == len(data.buildP)


def test_genGridData4():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=6,
                 numbCols=6)
    assert 36 == len(data.buildP)


def test_genGridData5():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=6,
                 numbCols=12)
    assert 72 == len(data.buildP)


def test_genGridData6():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=1,
                 numbCols=12)
    assert 0 == len(data.buildP)


def test_genGridData7():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=5,
                 numbCols=1)
    assert 0 == len(data.buildP)


def test_genGridData8():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=10,
                 numbCols=12)
    assert 0 == len(data.buildP)


def test_genGridData9():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=6,
                 numbCols=20)
    assert 0 == len(data.buildP)


def test_genInitial1():
    suc = data.genInitial(alt=30,
                          azStart=30,
                          numb=5,
                          )
    assert suc


def test_genInitial2():
    suc = data.genInitial(alt=0,
                          azStart=30,
                          numb=5,
                          )
    assert not suc


def test_genInitial3():
    suc = data.genInitial(alt=30,
                          azStart=-10,
                          numb=5,
                          )
    assert not suc


def test_genInitial4():
    suc = data.genInitial(alt=30,
                          azStart=30,
                          numb=2,
                          )
    assert not suc


def test_genInitial5():
    suc = data.genInitial(alt=30,
                          azStart=30,
                          numb=30,
                          )
    assert not suc


def test_isAboveHorizon():
    data.clearHorizonP()
    suc = data.isAboveHorizon((10, 50))
    assert suc
    suc = data.isAboveHorizon((10, 370))
    assert suc
    suc = data.isAboveHorizon((10, -50))
    assert suc
    suc = data.isAboveHorizon((-10, 50))
    assert not suc


def test_deleteBelowHorizon1():
    data.clearHorizonP()
    data.buildP = [(10, 10), (-5, 40), (40, 60)]
    data.deleteBelowHorizon()
    assert len(data.buildP) == 2


def test_deleteBelowHorizon2():
    data.clearHorizonP()
    data.buildP = [(10, 10), (5, 40), (-40, 60)]
    data.deleteBelowHorizon()
    assert len(data.buildP) == 2


def test_deleteBelowHorizon3():
    data.clearHorizonP()
    data.buildP = [(-10, 10), (5, 40), (40, 60)]
    data.deleteBelowHorizon()
    assert len(data.buildP) == 2


def test_deleteBelowHorizon4():
    data.clearHorizonP()
    data.buildP = [(-10, 10), (-5, 40), (-40, 60)]
    data.deleteBelowHorizon()
    assert len(data.buildP) == 0
