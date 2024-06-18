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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import os
from unittest import mock


# external packages
from PySide6.QtWidgets import QWidget, QComboBox, QTableWidget, QGroupBox

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWmixin.astroObjects import AstroObjects

satBaseUrl = 'http://www.celestrak.org/NORAD/elements/gp.php?'
satSourceURLs = {
    '100 brightest': {
        'url': satBaseUrl + 'GROUP=visual&FORMAT=tle',
        'file': 'visual.txt',
        'unzip': False,
        },
}


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    def test():
        pass

    function = AstroObjects(
        window=QWidget(),
        app=App(),
        objectText='test',
        sourceUrls=satSourceURLs,
        uiObjectList=QTableWidget(),
        uiSourceList=QComboBox(),
        uiSourceGroup=QGroupBox(),
        processFunc=test,
    )
    yield function


def test_buildSourceListDropdown_1(function):
    with mock.patch.object(function,
                           'loadSourceUrl'):
        function.buildSourceListDropdown()
        assert function.uiSourceList.count() == 1


def test_setAge_1(function):
    function.setAge(0)
    assert function.uiSourceGroup.title() == 'test data - age: 0.0d'


def test_loadSourceUrl_1(function):
    function.uiSourceList.clear()
    function.loadSourceUrl()


def test_loadSourceUrl_2(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem('100 brightest')
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(function.loader,
                               'days_old',
                               return_value=0):
            with mock.patch.object(function,
                                   'procSourceData'):
                function.loadSourceUrl()

