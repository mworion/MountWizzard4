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
import unittest.mock as mock
import pytest
import faulthandler
faulthandler.enable()

# external packages
import PyQt5
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QLineEdit
from skyfield.toposlib import Topos
from skyfield.api import Angle
import mountcontrol
from mountcontrol.qtmount import Mount
import matplotlib
import matplotlib.pyplot as plt

# local import
from mw4.gui.hemisphereW import HemisphereWindow
from mw4.imaging.camera import Camera
from mw4.dome.dome import Dome
from mw4.modeldata.buildpoints import DataPoint
from mw4.modeldata.hipparcos import Hipparcos
from mw4.astrometry.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app

    class Test2(QObject):
        threadPool = QThreadPool()
        update1s = pyqtSignal()

        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData='mw4/test/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

    class Test1a:
        checkDomeGeometry = QCheckBox()
        statusDualAxisTracking = QLineEdit()

    class Test1:
        deviceStat = {'dome': True}
        ui = Test1a()

    class Test(QObject):
        config = {'mainW': {},
                  'showHemisphereW': True}
        uiWindows = {'showImageW': {}}
        mwGlob = {'imageDir': 'mw4/test/image'}

        update1s = pyqtSignal()
        update10s = pyqtSignal()
        update0_1s = pyqtSignal()
        redrawHemisphere = pyqtSignal()
        message = pyqtSignal(str, int)

        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData='mw4/test/data')
        mount.obsSite.Alt = Angle(degrees=45)
        mount.obsSite.Az = Angle(degrees=45)
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

        camera = Camera(app=Test2())
        dome = Dome(app=Test2())
        astrometry = Astrometry(app=Test2())
        data = DataPoint(app=Test2(), configDir='mw4/test/config')
        hipparcos = Hipparcos(app=Test2())
        mainW = Test1()

    with mock.patch.object(HemisphereWindow,
                           'show'):
        app = HemisphereWindow(app=Test())
        qtbot.addWidget(app)
        yield


def test_markerPoint():
    val = app.markerPoint()
    assert isinstance(val, matplotlib.path.Path)


def test_markerAltAz():
    val = app.markerAltAz()
    assert isinstance(val, matplotlib.path.Path)


def test_markerStar():
    val = app.markerStar()
    assert isinstance(val, matplotlib.path.Path)


def test_configOperationMode_1():
    app.ui.checkShowAlignStar.setChecked(True)
    app.configOperationMode()
    assert app.ui.checkPolarAlignment.isEnabled()


def test_configOperationMode_2():
    app.ui.checkShowAlignStar.setChecked(False)
    app.ui.checkPolarAlignment.setChecked(False)
    app.configOperationMode()
    assert not app.ui.checkPolarAlignment.isEnabled()


def test_configOperationMode_3():
    app.ui.checkShowAlignStar.setChecked(False)
    app.ui.checkPolarAlignment.setChecked(True)
    app.configOperationMode()
    assert not app.ui.checkPolarAlignment.isEnabled()
    assert app.ui.checkEditNone.isChecked()


def test_setOperationMode_1():
    assert app.MODE is not None
    assert 'normal' in app.MODE
    assert 'build' in app.MODE
    assert 'horizon' in app.MODE
    assert 'star' in app.MODE


def test_setOperationMode_2():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.ui.checkEditNone.setChecked(True)
    app.horizonMarker = Test()
    app.pointsBuild = Test()
    suc = app.setOperationMode()
    assert suc


def test_setOperationMode_3():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.ui.checkEditHorizonMask.setChecked(True)
    app.horizonMarker = Test()
    app.pointsBuild = Test()
    suc = app.setOperationMode()
    app.ui.checkEditNone.setChecked(True)
    assert suc


def test_getIndexPoint_0():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = []
    epsilon = 0
    index = app.getIndexPoint(event=event,
                              plane=plane,
                              epsilon=epsilon,
                              )
    assert not index


def test_getIndexPoint_1():
    event = None
    plane = None
    epsilon = 0
    index = app.getIndexPoint(event=event,
                              plane=plane,
                              epsilon=epsilon,
                              )
    assert not index


def test_getIndexPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = None
    epsilon = 0
    index = app.getIndexPoint(event=event,
                              plane=plane,
                              epsilon=epsilon,
                              )
    assert not index


def test_getIndexPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 0
    index = app.getIndexPoint(event=event,
                              plane=plane,
                              epsilon=epsilon,
                              )
    assert not index


def test_getIndexPoint_4():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 200
    index = app.getIndexPoint(event=event,
                              plane=plane,
                              epsilon=epsilon,
                              )
    assert index == 0


def test_getIndexPoint_5():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 200
    index = app.getIndexPoint(event=event,
                              plane=plane,
                              epsilon=epsilon,
                              )
    assert index == 1


def test_getIndexPointX_1():
    event = None
    plane = None
    index = app.getIndexPointX(event=event,
                               plane=plane,
                               )
    assert not index


def test_getIndexPointX_2():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = None
    index = app.getIndexPointX(event=event,
                               plane=plane,
                               )
    assert not index


def test_getIndexPointX_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    index = app.getIndexPointX(event=event,
                               plane=plane,
                               )
    assert index == 0


def test_getIndexPointX_4():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    index = app.getIndexPointX(event=event,
                               plane=plane,
                               )
    assert index == 0


def test_getIndexPointX_5():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 180), (45, 360)]
    index = app.getIndexPointX(event=event,
                               plane=plane,
                               )
    assert index == 1


def test_getIndexPointX_6():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0)]
    index = app.getIndexPointX(event=event,
                               plane=plane,
                               )
    assert not index


def test_showMouseCoordinates_1():
    class Test:
        xdata = None
        ydata = None

    suc = app.showMouseCoordinates(Test())
    assert not suc


def test_showMouseCoordinates_2():
    class Test:
        xdata = 1
        ydata = None

    suc = app.showMouseCoordinates(Test())
    assert not suc


def test_showMouseCoordinates_3():
    class Test:
        xdata = 1
        ydata = 1

    suc = app.showMouseCoordinates(Test())
    assert suc


def test_onMouseNormal_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        suc = app.onMouseNormal(event=event)
        assert not suc


def test_onMouseNormal_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 0
    event.dblclick = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseNormal(event=event)
        assert not suc


def test_onMouseNormal_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseNormal(event=event)
        assert not suc


def test_onMouseNormal_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 0
    event.dblclick = True
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseNormal(event=event)
        assert not suc


def test_onMouseNormal_5():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseNormal(event=event)
        assert not suc


def test_onMouseNormal_6():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                suc = app.onMouseNormal(event=event)
                assert not suc


def test_onMouseNormal_7():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                with mock.patch.object(app.app.mount.obsSite,
                                       'startSlewing',
                                       return_value=True):
                    suc = app.onMouseNormal(event=event)
                    assert suc


def test_onMouseNormal_8():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    app.app.mainW.ui.checkDomeGeometry.setChecked(True)
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                with mock.patch.object(app.app.mount.obsSite,
                                       'startSlewing',
                                       return_value=True):
                    suc = app.onMouseNormal(event=event)
                    assert suc


def test_onMouseNormal_9():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    app.app.mainW.ui.checkDomeGeometry.setChecked(False)
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                with mock.patch.object(app.app.mount.obsSite,
                                       'startSlewing',
                                       return_value=True):
                    suc = app.onMouseNormal(event=event)
                    assert suc


def test_addHorizonPoint_1():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.addHorizonPoint(data=app.app.data, event=event)
    assert suc


def test_addHorizonPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.horizonP = [(0, 0)]
    suc = app.addHorizonPoint(data=app.app.data, event=event)
    assert suc


def test_addHorizonPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    suc = app.addHorizonPoint(data=app.app.data, event=event)
    assert suc


def test_deleteHorizonPoint_1():
    class Test:
        pass
    event = Test()
    event.xdata = 10
    event.ydata = 10
    app.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.deleteHorizonPoint(data=app.app.data, event=event)
    assert suc


def test_deleteHorizonPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.deleteHorizonPoint(data=app.app.data, event=event)
    assert not suc


def test_deleteHorizonPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.horizonP = [(0, 0)]
    suc = app.deleteHorizonPoint(data=app.app.data, event=event)
    assert not suc


def test_editHorizonMask_1():
    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 1
    app.horizonMarker = Test()
    app.horizonFill = Test()
    suc = app.editHorizonMask(data=app.app.data, event=event)
    assert suc


def test_editHorizonMask_2():
    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 3
    app.horizonMarker = Test()
    app.horizonFill = Test()
    app.app.data.horizonP = [(0, 0), (45, 180), (0, 360)]

    suc = app.editHorizonMask(data=app.app.data, event=event)
    assert suc


def test_editHorizonMask_3():
    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 2
    app.horizonMarker = Test()
    app.horizonFill = Test()
    suc = app.editHorizonMask(data=app.app.data, event=event)
    assert not suc


def test_addBuildPoint_1():
    suc = app.addBuildPoint()
    assert not suc


def test_addBuildPoint_2():
    app.app.data.buildP = []

    suc = app.addBuildPoint(data=app.app.data)
    assert not suc


def test_addBuildPoint_3():
    class Test:
        xdata = 10
        ydata = 10

    axes = plt.axes(label=1)
    app.app.data.buildP = []
    app.ui.checkShowSlewPath.setChecked(True)

    suc = app.addBuildPoint(data=app.app.data, event=Test(), axes=axes)
    assert suc


def test_addBuildPoint_4():
    class Test:
        xdata = 10
        ydata = 10

    axes = plt.axes(label=2)
    app.app.data.buildP = []
    app.ui.checkShowSlewPath.setChecked(False)

    suc = app.addBuildPoint(data=app.app.data, event=Test(), axes=axes)
    assert suc


def test_addBuildPoint_5():
    class Test:
        xdata = 10
        ydata = 10

    axes = plt.axes(label=3)
    app.app.data.buildP = []
    app.ui.checkShowSlewPath.setChecked(False)

    with mock.patch.object(app.app.data,
                           'addBuildP',
                           return_value=False):
        suc = app.addBuildPoint(data=app.app.data, event=Test(), axes=axes)
        assert not suc


def test_deleteBuildPointPoint_1():
    axes = app.hemisphereMat.figure.axes[0]
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        pass
    event = Test()
    event.xdata = 10
    event.ydata = 10
    app.app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    suc = app.deleteBuildPoint(data=app.app.data, event=event)
    assert suc


def test_deleteBuildPointPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    suc = app.deleteBuildPoint(data=app.app.data, event=event)
    assert not suc


def test_editBuildPoints_1():
    app.app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    axes = app.hemisphereMat.figure.axes[0]
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 1
    app.pointsBuild = Test()
    suc = app.editBuildPoints(data=app.app.data, event=event, axes=axes)
    assert suc


def test_editBuildPoints_2():
    app.app.data.buildP = [(0, 0), (10, 10), (45, 180)]
    axes = app.hemisphereMat.figure.axes[0]
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(180, 45)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(45, 180)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 3
    app.pointsBuild = Test()
    suc = app.editBuildPoints(data=app.app.data, event=event, axes=axes)
    assert suc


def test_editBuildPoints_3():
    app.app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    axes = app.hemisphereMat.figure.axes[0]
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 2
    app.pointsBuild = Test()
    suc = app.editBuildPoints(data=app.app.data, event=event, axes=axes)
    assert not suc


def test_onMouseEdit_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    suc = app.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    suc = app.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_2b():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = True
    suc = app.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=True):
            suc = app.onMouseEdit(event=event)
            assert not suc


def test_onMouseEdit_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(True)
    app.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=True):
            suc = app.onMouseEdit(event=event)
            assert suc


def test_onMouseEdit_5():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=True):
            suc = app.onMouseEdit(event=event)
            assert suc


def test_onMouseEdit_6():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(True)
    app.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=False):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=True):
            suc = app.onMouseEdit(event=event)
            assert not suc


def test_onMouseEdit_7():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=False):
            suc = app.onMouseEdit(event=event)
            assert not suc


def test_onMouseStar_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    event.dblclick = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        suc = app.onMouseStar(event=event)
        assert not suc


def test_onMouseStar_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 2
    event.dblclick = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseStar(event=event)
        assert not suc


def test_onMouseStar_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseStar(event=event)
        assert not suc


def test_onMouseStar_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseStar(event=event)
        assert not suc


def test_onMouseStar_5():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            suc = app.onMouseStar(event=event)
            assert not suc


def test_onMouseStar_6():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=True):
                suc = app.onMouseStar(event=event)
                assert not suc


def test_onMouseStar_7():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = []
    app.app.hipparcos.alt = []
    app.app.hipparcos.name = []
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseStar(event=event)
        assert not suc


def test_onMouseStar_8():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=False):
                suc = app.onMouseStar(event=event)
                assert not suc


def test_onMouseStar_9():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 3
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=True):
                suc = app.onMouseStar(event=event)
                assert not suc


def test_onMouseStar_10():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 3
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    app.app.mainW.ui.checkDomeGeometry.setChecked(True)
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=True):
                suc = app.onMouseStar(event=event)
                assert not suc


def test_onMouseStar_11():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 3
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    app.app.mainW.ui.checkDomeGeometry.setChecked(False)
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=True):
                suc = app.onMouseStar(event=event)
                assert not suc


def test_onMouseDispatcher_1():
    class Test:
        inaxes = True
        button = 1
        dblclick = False
        xdata = 180
        ydata = 45

    event = Test()
    app.ui.checkEditNone.setChecked(True)
    app.ui.checkEditBuildPoints.setChecked(True)
    app.ui.checkEditHorizonMask.setChecked(True)
    app.ui.checkPolarAlignment.setChecked(True)

    app.onMouseDispatcher(event=event)


def test_onMouseDispatcher_2():
    class Test:
        inaxes = True
        button = 1
        dblclick = False
        xdata = 180
        ydata = 45

    event = Test()
    app.ui.checkEditNone.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(True)
    app.ui.checkEditHorizonMask.setChecked(True)
    app.ui.checkPolarAlignment.setChecked(True)

    app.onMouseDispatcher(event=event)


def test_onMouseDispatcher_3():
    class Test:
        inaxes = True
        button = 1
        dblclick = False
        xdata = 180
        ydata = 45

    event = Test()
    app.ui.checkEditNone.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(False)
    app.ui.checkEditHorizonMask.setChecked(True)
    app.ui.checkPolarAlignment.setChecked(True)

    app.onMouseDispatcher(event=event)


def test_onMouseDispatcher_4():
    class Test:
        inaxes = True
        button = 1
        dblclick = False
        xdata = 180
        ydata = 45

    event = Test()
    app.ui.checkEditNone.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(False)
    app.ui.checkEditHorizonMask.setChecked(False)
    app.ui.checkPolarAlignment.setChecked(True)

    app.onMouseDispatcher(event=event)
