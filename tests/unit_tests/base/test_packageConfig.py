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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import platform

# external packages

# local import
from base.packageConfig import excludedPlatforms, checkAutomation


def test_config():
    assert 'armv7l' in excludedPlatforms
    assert 'aarch64' in excludedPlatforms


def test_checkAutomation_1():
    with mock.patch.object(platform,
                           'python_version',
                           return_value='3.8.1'):
        with mock.patch.object(platform,
                               'system',
                               return_value='Windows'):
            suc = checkAutomation()
            assert not suc


def test_checkAutomation_2():
    with mock.patch.object(platform,
                           'python_version',
                           return_value='3.8.2'):
        with mock.patch.object(platform,
                               'system',
                               return_value='Windows'):
            suc = checkAutomation()
            assert suc


def test_checkAutomation_3():
    with mock.patch.object(platform,
                           'python_version',
                           return_value='3.8.10'):
        with mock.patch.object(platform,
                               'system',
                               return_value='Windows'):
            suc = checkAutomation()
            assert suc


def test_checkAutomation_4():
    with mock.patch.object(platform,
                           'python_version',
                           return_value='3.8.10'):
        with mock.patch.object(platform,
                               'system',
                               return_value='Darwin'):
            suc = checkAutomation()
            assert not suc
