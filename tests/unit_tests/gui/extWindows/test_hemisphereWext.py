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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestSetupExtWindows import App
from gui.extWindows.hemisphereW import HemisphereWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = HemisphereWindow(app=App())
    yield window


def test_markerPoint(function):
    function.markerPoint()


def test_markerAltAz(function):
    function.markerAltAz()


def test_markerStar(function):
    function.markerStar()


def test_setOperationMode_1(function):
    function.ui.checkEditNone.setChecked(True)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.setOperationMode()
        assert suc
        assert function.operationMode == 'normal'


def test_setOperationMode_2(function):
    function.ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.setOperationMode()
        assert suc
        assert function.operationMode == 'build'


def test_setOperationMode_3(function):
    function.ui.checkEditHorizonMask.setChecked(True)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.setOperationMode()
        assert suc
        assert function.operationMode == 'horizon'


def test_setOperationMode_4(function):
    function.ui.checkPolarAlignment.setChecked(True)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.setOperationMode()
        assert suc
        assert function.operationMode == 'star'


def test_enableEditPoints_1(function):
    suc = function.enableEditPoints(True)
    assert suc


def test_enableEditPoints_2(function):
    suc = function.enableEditPoints(False)
    assert suc


def test_showMouseCoordinates_1(function):
    class Event:
        inaxes = False

    suc = function.showMouseCoordinates(Event())
    assert suc


def test_showMouseCoordinates_2(function):
    class Event:
        inaxes = True
        xdata = 10
        ydata = 10

    suc = function.showMouseCoordinates(Event())
    assert suc
    assert function.ui.azimuth.text() == '10.0'
    assert function.ui.altitude.text() == '10.0'


def test_slewSelectedTarget_1(function):
    function.app.deviceStat['dome'] = False
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=0):
            suc = function.slewSelectedTarget('test')
            assert not suc


def test_slewSelectedTarget_2(function):
    function.app.deviceStat['dome'] = False
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=5):
            suc = function.slewSelectedTarget('test')
            assert not suc


def test_slewSelectedTarget_3(function):
    function.app.deviceStat['dome'] = True
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=5):
            with mock.patch.object(function.app.mount.obsSite,
                                   'startSlewing',
                                   return_value=True):
                suc = function.slewSelectedTarget('test')
                assert suc


def test_onMouseNormal_1(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = False
        dblclick = False
        button = 0

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_2(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 0

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_3(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_4(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.onMouseNormal(Event())
        assert not suc


def test_onMouseNormal_5(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTarget',
                               return_value=False):
            suc = function.onMouseNormal(Event())
            assert not suc


def test_onMouseNormal_6(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTarget',
                               return_value=True):
            with mock.patch.object(function.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                suc = function.onMouseNormal(Event())
                assert suc


def test_addHorizonPointManual_0(function):
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = None
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=None):
        with mock.patch.object(function.app.data,
                               'addHorizonP',
                               return_value=False):
            with mock.patch.object(function,
                                   'drawHemisphere'):
                suc = function.addHorizonPointManual()
                assert not suc


def test_addHorizonPointManual_1(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=None):
        with mock.patch.object(function.app.data,
                               'addHorizonP',
                               return_value=False):
            with mock.patch.object(function,
                                   'drawHemisphere'):
                suc = function.addHorizonPointManual()
                assert not suc


def test_addHorizonPointManual_2(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'addHorizonP',
                               return_value=False):
            with mock.patch.object(function,
                                   'drawHemisphere'):
                suc = function.addHorizonPointManual()
                assert not suc


def test_addHorizonPointManual_3(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'addHorizonP',
                               return_value=True):
            with mock.patch.object(function,
                                   'drawHemisphere'):
                suc = function.addHorizonPointManual()
                assert suc


def test_addHorizonPoint_1(function):
    class Event:
        xdata = 10
        ydata = 10
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=None):
        with mock.patch.object(function.app.data,
                               'addHorizonP',
                               return_value=False):
            suc = function.addHorizonPoint(data=function.app.data, event=Event())
            assert not suc


def test_addHorizonPoint_2(function):
    class Event:
        xdata = 10
        ydata = 10
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'addHorizonP',
                               return_value=False):
            suc = function.addHorizonPoint(data=function.app.data, event=Event())
            assert not suc


def test_addHorizonPoint_3(function):
    class Event:
        xdata = 10
        ydata = 10
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'addHorizonP',
                               return_value=True):
            suc = function.addHorizonPoint(data=function.app.data, event=Event())
            assert suc


def test_deleteHorizonPoint_1(function):
    class Event:
        xdata = 10
        ydata = 10
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=None):
        with mock.patch.object(function.app.data,
                               'delHorizonP',
                               return_value=False):
            suc = function.deleteHorizonPoint(data=function.app.data, event=Event())
            assert not suc


def test_deleteHorizonPoint_2(function):
    class Event:
        xdata = 10
        ydata = 10
    function.app.data.horizonP = [(0, 0), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'delHorizonP',
                               return_value=False):
            suc = function.deleteHorizonPoint(data=function.app.data, event=Event())
            assert not suc


def test_deleteHorizonPoint_3(function):
    class Event:
        xdata = 10
        ydata = 10
    function.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'delHorizonP',
                               return_value=False):
            suc = function.deleteHorizonPoint(data=function.app.data, event=Event())
            assert not suc


def test_deleteHorizonPoint_4(function):
    class Event:
        xdata = 10
        ydata = 10
    function.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    with mock.patch.object(function,
                           'getIndexPointX',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'delHorizonP',
                               return_value=True):
            suc = function.deleteHorizonPoint(data=function.app.data, event=Event())
            assert suc


def test_editHorizonMask_1(function):
    class Event:
        button = 1

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.horizonMarker, = axe.plot(0, 0)
    function.horizonFill, = axe.fill([0, 1, 2], [0, 1, 2])
    function.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    with mock.patch.object(function,
                           'addHorizonPoint',
                           return_value=False):
        with mock.patch.object(function,
                               'drawHemisphere'):
            suc = function.editHorizonMask(data=function.app.data, event=Event())
            assert not suc


def test_editHorizonMask_2(function):
    class Event:
        button = 3

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.horizonMarker, = axe.plot(0, 0)
    function.horizonFill, = axe.fill([0, 1, 2], [0, 1, 2])
    function.app.data.horizonP = None
    with mock.patch.object(function,
                           'deleteHorizonPoint',
                           return_value=False):
        suc = function.editHorizonMask(data=function.app.data, event=Event())
        assert not suc


def test_editHorizonMask_3(function):
    class Event:
        button = 0

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.horizonMarker, = axe.plot(0, 0)
    function.horizonFill, = axe.fill([0, 1, 2], [0, 1, 2])
    suc = function.editHorizonMask(data=function.app.data, event=Event())
    assert not suc


def test_addBuildPoint_1(function):
    class Event:
        button = 0
        xdata = 10
        ydata = 10

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    data = function.app.data

    with mock.patch.object(function,
                           'getIndexPoint',
                           return_value=None):
        suc = function.addBuildPoint(data=data, event=Event())
        assert not suc


def test_addBuildPoint_2(function):
    class Event:
        button = 0
        xdata = 10
        ydata = 10

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    data = function.app.data

    with mock.patch.object(function,
                           'getIndexPoint',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'addBuildP',
                               return_value=False):
            suc = function.addBuildPoint(data=data, event=Event())
            assert not suc


def test_addBuildPoint_3(function):
    class Event:
        xdata = 10
        ydata = 10
        button = 0

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    data = function.app.data

    with mock.patch.object(function,
                           'getIndexPoint',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'addBuildP',
                               return_value=True):
            suc = function.addBuildPoint(data=data, event=Event())
            assert suc


def test_addBuildPoint_4(function):
    class Event:
        xdata = 10
        ydata = 10
        button = 0

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    data = function.app.data
    function.ui.checkShowSlewPath.setChecked(True)
    function.pointsBuildAnnotate = None

    with mock.patch.object(function,
                           'getIndexPoint',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'addBuildP',
                               return_value=True):
            suc = function.addBuildPoint(data=data, event=Event())
            assert suc


def test_deleteBuildPoint_1(function):
    class Event:
        xdata = 10
        ydata = 10
        button = 0
    data = function.app.data
    with mock.patch.object(function,
                           'getIndexPoint',
                           return_value=None):
        with mock.patch.object(function.app.data,
                               'delBuildP',
                               return_value=False):
            suc = function.deleteBuildPoint(data=data, event=Event())
            assert not suc


def test_deleteBuildPoint_2(function):
    class Event:
        xdata = 10
        ydata = 10
        button = 0
    data = function.app.data
    with mock.patch.object(function,
                           'getIndexPoint',
                           return_value=1):
        with mock.patch.object(function.app.data,
                               'delBuildP',
                               return_value=False):
            suc = function.deleteBuildPoint(data=data, event=Event())
            assert not suc


def test_deleteBuildPoint_3(function):
    class Event:
        xdata = 10
        ydata = 10
        button = 0
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointsBuildAnnotate = [axe.annotate('test', (0, 0))]
    function.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    data = function.app.data
    with mock.patch.object(function,
                           'getIndexPoint',
                           return_value=0):
        with mock.patch.object(function.app.data,
                               'delBuildP',
                               return_value=True):
            suc = function.deleteBuildPoint(data=data, event=Event())
            assert suc


def test_editBuildPoints_1(function):
    class Event:
        button = 1

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointsBuild, = axe.plot(0, 0)
    function.app.data.buildP = [(0, 0, True), (1, 1, True)]
    function.pointsBuildAnnotate = [axe.annotate('test', (0, 0)),
                                    axe.annotate('test', (0, 0))]
    with mock.patch.object(function,
                           'addBuildPoint',
                           return_value=False):
        with mock.patch.object(function,
                               'drawHemisphere'):
            suc = function.editBuildPoints(data=function.app.data, event=Event())
            assert not suc


def test_editBuildPoints_2(function):
    class Event:
        button = 3

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointsBuild, = axe.plot([0, 1], [0, 1])
    function.app.data.buildP = [(0, 0, True), (1, 1, True)]
    function.pointsBuildAnnotate = [axe.annotate('test', (0, 0)),
                                    axe.annotate('test', (0, 0))]
    with mock.patch.object(function,
                           'deleteBuildPoint',
                           return_value=False):
        with mock.patch.object(function,
                               'drawHemisphere'):
            suc = function.editBuildPoints(data=function.app.data, event=Event())
            assert not suc


def test_editBuildPoints_3(function):
    class Event:
        button = 0

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointsBuild, = axe.plot(0, 0)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.editBuildPoints(data=function.app.data, event=Event())
        assert not suc


def test_editBuildPoints_4(function):
    class Event:
        button = 3

    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointsBuild, = axe.plot([0, 1], [0, 1])
    function.app.data.buildP = []
    function.pointsBuildAnnotate = [axe.annotate('test', (0, 0)),
                                    axe.annotate('test', (0, 0))]
    with mock.patch.object(function,
                           'deleteBuildPoint',
                           return_value=False):
        with mock.patch.object(function,
                               'drawHemisphere'):
            suc = function.editBuildPoints(data=function.app.data, event=Event())
            assert not suc


def test_onMouseEdit_1(function):
    function.generateFlat(widget=function.hemisphereMat, horizon=False)

    class Event:
        inaxes = False
        dblclick = False

    suc = function.onMouseEdit(Event())
    assert not suc


def test_onMouseEdit_2(function):
    function.generateFlat(widget=function.hemisphereMat, horizon=False)

    class Event:
        inaxes = True
        dblclick = True

    suc = function.onMouseEdit(Event())
    assert not suc


def test_onMouseEdit_3(function):
    function.ui.checkEditHorizonMask.setChecked(True)
    function.ui.checkEditBuildPoints.setChecked(False)
    function.generateFlat(widget=function.hemisphereMat, horizon=False)

    class Event:
        inaxes = True
        dblclick = False

    with mock.patch.object(function,
                           'editHorizonMask',
                           return_value=True):
        suc = function.onMouseEdit(Event())
        assert suc


def test_onMouseEdit_4(function):
    function.ui.checkEditHorizonMask.setChecked(False)
    function.ui.checkEditBuildPoints.setChecked(True)
    function.generateFlat(widget=function.hemisphereMat, horizon=False)

    class Event:
        inaxes = True
        dblclick = False

    with mock.patch.object(function,
                           'editBuildPoints',
                           return_value=True):
        suc = function.onMouseEdit(Event())
        assert suc


def test_onMouseEdit_5(function):
    function.ui.checkEditHorizonMask.setChecked(False)
    function.ui.checkEditBuildPoints.setChecked(False)
    function.generateFlat(widget=function.hemisphereMat, horizon=False)

    class Event:
        inaxes = True
        dblclick = False

    suc = function.onMouseEdit(Event())
    assert not suc


def test_onMouseStar_1(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = False
        dblclick = False
        button = 0

    suc = function.onMouseStar(Event())
    assert not suc


def test_onMouseStar_2(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    suc = function.onMouseStar(Event())
    assert not suc


def test_onMouseStar_2b(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 3

    function.app.mount.model.numberStars = 3
    suc = function.onMouseStar(Event())
    assert not suc


def test_onMouseStar_3(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 3

    function.app.mount.model.numberStars = 3
    suc = function.onMouseStar(Event())
    assert not suc


def test_onMouseStar_4(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=None):
            suc = function.onMouseStar(Event())
            assert not suc


def test_onMouseStar_5(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 3

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=None):
            suc = function.onMouseStar(Event())
            assert not suc


def test_onMouseStar_6(function):
    function.app.hipparcos.name = ['test']

    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                suc = function.onMouseStar(Event())
                assert not suc


def test_onMouseStar_7(function):
    function.app.hipparcos.name = ['test']

    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                with mock.patch.object(function,
                                       'slewSelectedTarget',
                                       return_value=False):
                    suc = function.onMouseStar(Event())
                    assert not suc


def test_onMouseStar_8(function):
    function.app.hipparcos.name = ['test']

    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                with mock.patch.object(function,
                                       'slewSelectedTarget',
                                       return_value=True):
                    with mock.patch.object(function.app.mount.obsSite,
                                           'setTargetRaDec',
                                           return_value=True):
                        suc = function.onMouseStar(Event())
                        assert suc


def test_onMouseDispatcher_1(function):
    class Event:
        pass
    function.ui.checkEditNone.setChecked(True)

    with mock.patch.object(function,
                           'onMouseNormal'):
        suc = function.onMouseDispatcher(Event())
        assert suc


def test_onMouseDispatcher_2(function):
    class Event:
        pass
    function.ui.checkEditBuildPoints.setChecked(True)

    with mock.patch.object(function,
                           'onMouseEdit'):
        suc = function.onMouseDispatcher(Event())
        assert suc


def test_onMouseDispatcher_3(function):
    class Event:
        pass
    function.ui.checkEditHorizonMask.setChecked(True)

    with mock.patch.object(function,
                           'onMouseEdit'):
        suc = function.onMouseDispatcher(Event())
        assert suc


def test_onMouseDispatcher_4(function):
    class Event:
        pass
    function.ui.checkPolarAlignment.setChecked(True)

    with mock.patch.object(function,
                           'onMouseStar'):
        suc = function.onMouseDispatcher(Event())
        assert suc
