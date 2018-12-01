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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
# external packages
import PyQt5.QtWidgets
# local import
from mw4.environ import environ

test = PyQt5.QtWidgets.QApplication([])
host_ip = 'astro-mount.fritz.box'

app = environ.Environment(host_ip)


def test_localWeatherName():
    name = 'MBox'
    app.localWeatherName = name
    assert name == app.localWeatherName


def test_globalWeatherName():
    name = 'MBox'
    app.globalWeatherName = name
    assert name == app.globalWeatherName


def test_sqmName():
    name = 'MBox'
    app.sqmName = name
    assert name == app.sqmName


def test_newDevice1():
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=False):
        suc = app.newDevice('test')
        assert not suc


def test_newDevice2():
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.client,
                               'getDevice',
                               return_value=1):
            suc = app.newDevice('test')
            assert suc
            for wType in app.wDevice:
                assert None is app.wDevice[wType]['device']


def test_newDevice3():
    app.wDevice['local']['name'] = 'Test'
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.client,
                               'getDevice',
                               return_value=1):
            suc = app.newDevice('Test')
            assert suc
            assert None is not app.wDevice['local']['device']


def test_removeDevice1():
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=False):
        suc = app.removeDevice('test')
        assert not suc


def test_removeDevice2():
    app.wDevice['local']['name'] = 'Test'
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=True):
        suc = app.removeDevice('Test')
        assert suc
        assert None is app.wDevice['local']['device']
        assert {} == app.wDevice['local']['data']


def test_startCommunication1():
    app.localWeatherName = ''
    app.globalWeatherName = ''
    app.sqmName = ''

    with mock.patch.object(app.client,
                           'connectServer',
                           return_value=False):
        suc = app.startCommunication()
        assert not suc


def test_startCommunication2():
    app.sqmName = 'SQM'
    with mock.patch.object(app.client,
                           'connectServer',
                           return_value=True):
        suc = app.startCommunication()
        assert not suc


def test_startCommunication3():
    name = 'MBox'
    app.sqmName = name
    app.wDevice['local']['name'] = 'Test'
    with mock.patch.object(app.client,
                           'watchDevice',
                           return_value=True):
        with mock.patch.object(app.client,
                               'connectServer',
                               return_value=True):
            suc = app.startCommunication()
            assert suc
            app.client.watchDevice.assert_called_with('MBox')


def test_startCommunication4():
    app.wDevice['local']['name'] = 'Test'
    with mock.patch.object(app.client,
                           'watchDevice',
                           return_value=False):
        with mock.patch.object(app.client,
                               'connectServer',
                               return_value=True):
            suc = app.startCommunication()
            assert not suc


def test_startCommunication5():
    with mock.patch.object(app.client,
                           'watchDevice',
                           return_value=False):
        suc = app.startCommunication()
        assert not suc
        print(app.wDevice)






'''
        with qtbot.waitSignal(relay.statusReady) as blocker:
            relay.cyclePolling()
    assert [0, 0, 0, 0, 0, 0, 0, 0] == relay.status
'''