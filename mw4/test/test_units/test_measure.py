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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import numpy as np
# external packages
# local import
from mw4.test.test_units.setupQt import setupQt



@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_measureTask_1():
    app.mainW.ui.measureDevice.setCurrentIndex(1)
    app.environ.data = {}
    suc = app.measure._measureTask()
    assert suc
    assert app.measure.data['envTemp'].shape[0]
    assert app.measure.data['envHum'].shape[0]
    assert app.measure.data['envPress'].shape[0]
    assert app.measure.data['envDew'].shape[0]


def test_measureTask_2():
    app.mainW.ui.measureDevice.setCurrentIndex(0)
    app.environ.data = {}
    app.measure.data = {
        'time': np.empty(shape=[0, 1], dtype='datetime64'),
        'envTemp': np.empty(shape=[0, 1]),
        'envHum': np.empty(shape=[0, 1]),
        'envPress': np.empty(shape=[0, 1]),
        'envDew': np.empty(shape=[0, 1]),
        'skyTemp': np.empty(shape=[0, 1]),
        'skySQR': np.empty(shape=[0, 1]),
        'raJNow': np.empty(shape=[0, 1]),
        'decJNow': np.empty(shape=[0, 1]),
        'status': np.empty(shape=[0, 1]),
        'powCurr1': np.empty(shape=[0, 1]),
        'powCurr2': np.empty(shape=[0, 1]),
        'powCurr3': np.empty(shape=[0, 1]),
        'powCurr4': np.empty(shape=[0, 1]),
        'powVolt': np.empty(shape=[0, 1]),
        'powCurr': np.empty(shape=[0, 1]),
        'powHum': np.empty(shape=[0, 1]),
        'powTemp': np.empty(shape=[0, 1]),
        'powDew': np.empty(shape=[0, 1]),
    }
    suc = app.measure._measureTask()
    assert suc
    assert app.measure.data['envTemp'].shape[0] == 1
    assert app.measure.data['envHum'].shape[0] == 1
    assert app.measure.data['envPress'].shape[0] == 1
    assert app.measure.data['envDew'].shape[0] == 1


def test_measureTask_3():
    app.mainW.ui.measureDevice.setCurrentIndex(1)
    app.environ.data['WEATHER_TEMPERATURE'] = 10
    app.environ.data['WEATHER_PRESSURE'] = 1000
    app.environ.data['WEATHER_DEWPOINT'] = 10
    app.environ.data['WEATHER_HUMIDITY'] = 10
    suc = app.measure._measureTask()
    assert suc
    assert app.measure.data['envTemp'][1] == 10
    assert app.measure.data['envHum'][1] == 10
    assert app.measure.data['envPress'][1] == 1000
    assert app.measure.data['envDew'][1] == 10
    app.mainW.ui.measureDevice.setCurrentIndex(0)


def test_calculateReference_1():
    app.measure.raRef = 0
    app.measure.decRef = 0
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([])
    ra, dec = app.measure._calculateReference()
    assert ra == 0
    assert dec == 0


def test_calculateReference_2():
    app.measure.raRef = 0
    app.measure.decRef = 0
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 3600
    assert dec == 3600


def test_calculateReference_3():
    app.measure.raRef = 1800
    app.measure.decRef = 1800
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 1800
    assert dec == 1800


def test_calculateReference_4():
    app.measure.raRef = 1800
    app.measure.decRef = 1800
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 1, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 0
    assert dec == 0
    assert app.measure.raRef is None
    assert app.measure.decRef is None


def test_calculateReference_5():
    app.measure.raRef = None
    app.measure.decRef = None
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 0
    assert dec == 0
    assert app.measure.raRef is not None
    assert app.measure.decRef is not None


def test_calculateReference_6():
    app.measure.raRef = 0
    app.measure.decRef = 0
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 3600.0
    assert dec == 3600.0


def test_calculateReference_7():
    app.measure.raRef = 0
    app.measure.decRef = 0
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    ra, dec = app.measure._calculateReference()
    assert ra == 0.0
    assert dec == 0.0


def test_checkSize_1():
    app.measure.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['temp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['humidity'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['press'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['dewTemp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['sqr'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['raJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['decJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.MAXSIZE = 20
    suc = app.measure._checkSize()
    assert not suc


def test_checkSize_2():
    app.measure.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['temp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['humidity'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['press'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['dewTemp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['sqr'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['raJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['decJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.measure.MAXSIZE = 5
    suc = app.measure._checkSize()
    assert suc
