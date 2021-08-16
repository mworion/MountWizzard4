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

# external packages
import pytest

# local import
from base.alpacaBase import SafetyMonitor


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = SafetyMonitor()

    yield


def test_issafe():
    val = app.issafe()
    val is None

