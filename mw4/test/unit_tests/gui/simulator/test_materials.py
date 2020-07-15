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
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.Qt3DExtras import QSphereMesh
from PyQt5.Qt3DCore import QEntity

# local import
from mw4.gui.simulator.materials import Materials
from mw4.gui.simulator.materials import linkModel


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Materials()

    yield


def test_1():
    assert app.white


def test_linkModel_1():
    e = QEntity()
    model = {
        'pointer':
            {'parent': None,
             'source': [QSphereMesh(), 50, 30, 30],
             'scale': [1, 1, 1],
             'mat': Materials().pointer,
             }
    }

    for name in model:
        linkModel(model, name, e)

    assert 't' in model['pointer']
