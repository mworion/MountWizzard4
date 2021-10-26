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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import platform


# external packages


# local import
from gui.utilities.stylesQtCss import Styles


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = Styles()
    yield window


def test_renderStyle_1(function):
    inStyle = '12345$M_BLUE$12345'
    val = function.renderStyle(inStyle).strip(' ')
    assert val == '12345#2090C012345\n'


def test_renderStyle_2(function):
    inStyle = '12345$M_TEST$12345'
    val = function.renderStyle(inStyle).strip(' ')
    assert val == '12345$M_TEST$12345\n'


def test_getStyle_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        ret = function.mw4Style
        assert ret.startswith('\n')


def test_getStyle_2(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        ret = function.mw4Style
        assert ret.startswith('\n')
