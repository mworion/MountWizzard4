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
import pytest
import unittest.mock as mock
import platform

# external packages

# local import
from base.packageConfig import excludedPlatforms, checkMinimalPythonVersion


def test_config():
    assert 'armv7l' in excludedPlatforms
    assert 'aarch64' in excludedPlatforms


def test_checkMinimalPythonVersion_1():
    with mock.patch.object(platform,
                           'python_version',
                           return_value='3.8.2'):
        suc = checkMinimalPythonVersion('3.8.1')
        assert not suc


def test_checkMinimalPythonVersion_2():
    with mock.patch.object(platform,
                           'python_version',
                           return_value='3.8.2'):
        suc = checkMinimalPythonVersion('3.8.2')
        assert suc


def test_checkMinimalPythonVersion_3():
    with mock.patch.object(platform,
                           'python_version',
                           return_value='3.8.2'):
        suc = checkMinimalPythonVersion('3.8.10')
        assert suc
