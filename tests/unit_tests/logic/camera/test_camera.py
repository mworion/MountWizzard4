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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from astropy.io import fits
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidgets import sleepAndEvents
from logic.camera.camera import Camera
import logic


@pytest.fixture(autouse=True, scope='module')
def function():
    func = Camera(app=App())
    yield func


def test_properties(function):
    function.framework = 'indi'
    function.host = ('localhost', 7624)
    assert function.host == ('localhost', 7624)

    function.deviceName = 'test'
    assert function.deviceName == 'test'


def test_properties_1(function):
    function.data = {'CCD_BINNING.HOR_BIN': 1}
    function.binning = 0
    assert function.binning == 1


def test_properties_2(function):
    function.updateRate = 1000
    function.loadConfig = True
    function.framework = 'indi'
    assert function.updateRate == 1000
    assert function.loadConfig


def test_propSubFrame_0(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    function.subFrame = 1
    assert function.posX == 0
    assert function.posY == 0
    assert function.width == 1000
    assert function.height == 1000


def test_propSubFrame_1(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    function.subFrame = 90
    assert function.posX == 50
    assert function.posY == 50
    assert function.width == 900
    assert function.height == 900


def test_propSubFrame_2(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 100,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    function.subFrame = 100
    assert function.posX == 0
    assert function.posY == 0
    assert function.width == 100
    assert function.height == 1000


def test_propSubFrame_3(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 100}
    function.subFrame = 100
    assert function.posX == 0
    assert function.posY == 0
    assert function.width == 1000
    assert function.height == 100


def test_propSubFrame_4(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    function.subFrame = 50
    assert function.posX == 250
    assert function.posY == 250
    assert function.width == 500
    assert function.height == 500


def test_propSubFrame_5(function):
    function.binning = 2
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    function.subFrame = 100
    assert function.posX == 0
    assert function.posY == 0
    assert function.width == 1000
    assert function.height == 1000
    temp = function.subFrame


def test_setObsSite(function):
    function.setObsSite(function.app.mount.obsSite)


def test_exposeFinished(function):
    function.exposeFinished()


def test_startCommunication_1(function):
    function.framework = 'indi'
    suc = function.startCommunication()
    assert suc


def test_stopCommunication_1(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'abort',
                           return_value=True):
        suc = function.stopCommunication()
        assert suc


def test_expose_2(function):
    function.exposing = True
    function.framework = 'indi'
    suc = function.expose()
    assert not suc


def test_expose_3(function):
    function.exposing = False
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'expose',
                           return_value=True):
        suc = function.expose(imagePath='tests/workDir/image', subFrame=90)
        assert suc


def test_abort_2(function):
    function.framework = 'indi'
    function.exposing = True
    with mock.patch.object(function.run['indi'],
                           'abort',
                           return_value=True):
        function.abort()
        assert not function.exposing


def test_sendDownloadMode_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendDownloadMode',
                           return_value=True):
        function.sendDownloadMode()


def test_sendCoolerSwitch_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendCoolerSwitch',
                           return_value=True):
        function.sendCoolerSwitch()


def test_sendCoolerTemp_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendCoolerTemp',
                           return_value=True):
        function.sendCoolerTemp()


def test_sendOffset_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendOffset',
                           return_value=True):
        function.sendOffset()


def test_sendGain_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendGain',
                           return_value=True):
        function.sendGain()


def test_waitExposed_1(function):
    def test():
        function.exposing = False
        return

    function.waitExposed(1, test)


def test_waitExposed_2(function):
    def test():
        function.exposing = False
        return
        
    function.waitExposed(0.05, test)
    

def test_waitStart_1(function):
    def test():
        function.exposing = False
        return
        
    temp = function.sleepAndEvents 
    function.sleepAndEvents = test
    function.exposing = True
    function.waitStart()
    function.sleepAndEvents = temp
    
    
def test_waitDownload(function):
    def test():
        function.exposing = False
        return
        
    temp = function.sleepAndEvents 
    function.sleepAndEvents = test
    function.exposing = True
    function.waitDownload()
    function.sleepAndEvents = temp
    
    
def test_waitSave_1(function):
    def test():
        function.exposing = False
        return
        
    temp = function.sleepAndEvents 
    function.sleepAndEvents = test
    function.exposing = True
    function.waitSave()
    function.sleepAndEvents = temp
    

def test_waitFinish(function):   
    def test(a):
        function.exposing = False
        return
        
    function.exposing = True
    function.waitFinish(test, {})
    
    
def test_retrieveImage_1(function):
    function.exposing = False
    def test():
        return
        
    function.retrieveImage(test, {})
    
    
def test_retrieveImage_2(function):
    function.exposing = True
    def test(param):
        return
        
    function.retrieveImage(test, {})
    assert not function.exposing
    
    
def test_retrieveImage_3(function):
    function.exposing = True
    def test(param):
        return np.array([], dtype=np.uint16)
        
    function.retrieveImage(test, {})
    
    
def test_writeImageFitsHeader_1(function):
    with mock.patch.object(fits,
                           'open'):
       with mock.patch.object(logic.camera.camera,
                               'writeHeaderPointing'):
           with mock.patch.object(logic.camera.camera,
                                   'writeHeaderCamera'):
                function.updateImageFitsHeaderPointing()
    
    
def test_updateImageFitsHeaderPointing_1(function):
    with mock.patch.object(fits,
                           'open'):
       with mock.patch.object(logic.camera.camera,
                               'writeHeaderPointing'):
            function.updateImageFitsHeaderPointing()

