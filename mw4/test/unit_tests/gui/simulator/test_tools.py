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
from PyQt5.Qt3DExtras import QPhongMaterial
from PyQt5.Qt3DRender import QMesh
from PyQt5.Qt3DCore import QTransform


# local import
from mw4.gui.simulator.tools import linkModel
from mw4.gui.simulator.tools import linkMaterial
from mw4.gui.simulator.tools import linkSource
from mw4.gui.simulator.tools import linkTransform
from mw4.gui.simulator.materials import Materials


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    yield


def test_linkSource_1(qtbot):
    model = {'parent': None,
             'source': [QSphereMesh(), 50, 30, 30],
             }
    mesh = linkSource(model)

    assert isinstance(mesh, QSphereMesh)


def test_linkTransform_1(qtbot):
    model = {'parent': None,
             'scale': [1, 1, 1],
             }
    trans = linkTransform(model)

    assert isinstance(trans, QTransform)


def test_linkMaterial_1(qtbot):
    model = {'parent': None,
             'mat': Materials().pointer,
             }

    mat = linkMaterial(model)
    assert isinstance(mat, QPhongMaterial)


def test_linkModel_1(qtbot):
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
