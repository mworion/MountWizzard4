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
import pytest

# external packages

# local import
from base import packageConfig


def test_exclude():
    assert packageConfig.excludedPlatforms == ['armv7l']


def test_config():
    assert 'analyse' in packageConfig.featureFlags
    assert 'simulator' in packageConfig.featureFlags


