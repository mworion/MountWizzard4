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
# external packages
from PyQt5.Qt3DExtras import QSphereMesh, QCuboidMesh
from PyQt5.Qt3DCore import QEntity
from PyQt5.Qt3DExtras import QPhongMaterial, QCylinderMesh, QExtrudedTextMesh
from PyQt5.Qt3DCore import QTransform
from PyQt5.Qt3DRender import QMesh


# local import
from gui.extWindows.simulator.tools import linkModel
from gui.extWindows.simulator.tools import linkMaterial
from gui.extWindows.simulator.tools import linkSource
from gui.extWindows.simulator.tools import linkTransform
from gui.extWindows.simulator.materials import Materials


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    yield


def test_linkSource_1(qtbot):
    model = {'parent': None,
             'source': 'mount-ra.stl',
             }
    mesh = linkSource(model)
    assert isinstance(mesh, QMesh)


def test_linkSource_2(qtbot):
    model = {'parent': None,
             'source': [QSphereMesh(), 50, 30, 30],
             }
    mesh = linkSource(model)
    assert isinstance(mesh, QSphereMesh)


def test_linkSource_3(qtbot):
    model = {'parent': None,
             'source': [QCuboidMesh(), 50, 30, 30],
             }
    mesh = linkSource(model)
    assert isinstance(mesh, QCuboidMesh)


def test_linkSource_4(qtbot):
    model = {'parent': None,
             'source': [QCylinderMesh(), 50, 30, 30, 1],
             }
    mesh = linkSource(model)
    assert isinstance(mesh, QCylinderMesh)


def test_linkSource_5(qtbot):
    model = {'parent': None,
             'source': [QExtrudedTextMesh(), 30, 'Arial', 'test'],
             }
    mesh = linkSource(model)
    assert isinstance(mesh, QExtrudedTextMesh)


def test_linkSource_6(qtbot):
    model = {'parent': None,
             'source': [None, 30, 'Arial', 'test'],
             }
    mesh = linkSource(model)
    assert mesh is None


def test_linkSource_7(qtbot):
    model = {'parent': None,
             }
    mesh = linkSource(model)
    assert mesh is None


def test_linkTransform_1(qtbot):
    model = {'parent': None,
             'scale': [1, 1, 1],
             }
    trans = linkTransform(model)
    assert isinstance(trans, QTransform)


def test_linkTransform_2(qtbot):
    model = {'parent': None,
             'trans': [1, 1, 1],
             }
    trans = linkTransform(model)
    assert isinstance(trans, QTransform)


def test_linkTransform_3(qtbot):
    model = {'parent': None,
             'rot': [1, 1, 1],
             }
    trans = linkTransform(model)
    assert isinstance(trans, QTransform)


def test_linkTransform_4(qtbot):
    model = {'parent': None,
             }
    trans = linkTransform(model)
    assert trans is None


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
