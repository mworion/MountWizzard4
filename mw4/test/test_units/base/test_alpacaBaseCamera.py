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
from unittest import mock

# external packages
import pytest

# local import
from mw4.base.alpacaBase import Camera


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Camera()


def test_bayeroffsetx():
    val = app.bayeroffsetx()
    assert val is None

