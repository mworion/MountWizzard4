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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import pytest

# local import
from mw4.base.alpacaBase import SafetyMonitor


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = SafetyMonitor()

    yield


def test_issafe():
    val = app.issafe()
    assert val is None

