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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import logging

# external packages
import pytest
import requests

# local import
from base.alpacaBase import AlpacaBase
from base.loggerMW import addLoggingLevel


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = AlpacaBase()
    app.log = logging.getLogger()
    addLoggingLevel('TRACE', 5)

    yield


def test_properties_1():
    app.host = ('localhost', 11111)
    app.deviceName = 'test'
    app.deviceName = 'test:2'
    app.deviceName = 'test:2:3'
    app.apiVersion = 1
    app.protocol = 1


def test_properties_2():
    host = app.host
    assert host == ('localhost', 11111)
    assert app.deviceName == ''
    assert app.apiVersion == 1
    assert app.protocol == 'http'
    assert app.baseUrl == 'http://localhost:11111/api/v1//0'


def test_discoverAPIVersion_1():
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception()):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_1b():
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_1c():
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_2():
    class Test:
        status_code = 400
        text = 'test'

    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_3():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_4():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.discoverAPIVersion()
        assert val == 'test'


def test_discoverDevices_1():
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception()):
        val = app.discoverDevices()
        assert val is None


def test_discoverDevices_1b():
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout):
        val = app.discoverDevices()
        assert val is None


def test_discoverDevices_1c():
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError):
        val = app.discoverDevices()
        assert val is None


def test_discoverDevices_2():
    class Test:
        status_code = 400
        text = 'test'

    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.discoverDevices()
        assert val is None


def test_discoverDevices_3():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.discoverDevices()
        assert val is None


def test_discoverDevices_4():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.discoverDevices()
        assert val == 'test'


def test_get_1():
    val = app.get('')
    assert val is None


def test_get_2():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout,
                           return_value=Test()):
        val = app.get('')
        assert val is None


def test_get_2b():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError,
                           return_value=Test()):
        val = app.get('')
        assert val is None


def test_get_2c():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception(),
                           return_value=Test()):
        val = app.get('')
        assert val is None


def test_get_3():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.get('')
        assert val is None


def test_get_4():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg'}

    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.get('')
        assert val is None


def test_get_5():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.get('')
        assert val == 'test'


def test_put_1():
    val = app.put('')
    assert val is None


def test_put_2():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'put',
                           side_effect=Exception(),
                           return_value=Test()):
        val = app.put('')
        assert val is None


def test_put_2b():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'put',
                           side_effect=requests.exceptions.Timeout,
                           return_value=Test()):
        val = app.put('')
        assert val is None


def test_put_2c():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'put',
                           side_effect=requests.exceptions.ConnectionError,
                           return_value=Test()):
        val = app.put('')
        assert val is None


def test_put_3():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = app.put('')
        assert val is None


def test_put_4():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg'}

    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = app.put('')
        assert val is None


def test_put_5():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = app.put('')
        assert val == {'ErrorMessage': 'msg', 'ErrorNumber': 0, 'Value': 'test'}


def test_action():
    app.action(Action='test')


def test_commandblind():
    app.commandblind(Command='test', Raw='test')


def test_commandbool():
    app.commandbool(Command='test', Raw='test')


def test_commandstring():
    app.commandstring(Command='test', Raw='test')


def test_connected_1():
    app.connected(Connected=True)


def test_connected_2():
    app.connected(Connected=False)


def test_connected_3():
    val = app.connected()
    assert val is None


def test_description():
    val = app.description()
    assert val is None


def test_driverInfo_1():
    with mock.patch.object(app,
                           'get',
                           return_value=None):
        val = app.driverInfo()
        assert val == ''


def test_driverInfo_2():
    with mock.patch.object(app,
                           'get',
                           return_value='test   , 56, 45'):
        val = app.driverInfo()
        assert val == ['test', '56', '45']


def test_driverVersion():
    val = app.driverVersion()
    assert val is None


def test_interfaceVersion():
    val = app.interfaceVersion()
    assert val is None


def test_nameDevice():
    val = app.nameDevice()
    assert val is None


def test_supportedActions():
    val = app.supportedActions()
    assert val is None
