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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DExtras import Qt3DExtras


# local import
from gui.extWindows.simulator.tools import linkModel
from gui.extWindows.simulator.tools import linkMaterial
from gui.extWindows.simulator.tools import linkSource
from gui.extWindows.simulator.tools import linkTransform
from gui.extWindows.simulator.tools import getMaterial
from gui.extWindows.simulator.materials import Materials


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    yield


def test_linkSource_1(qtbot):
    model = {'parent': None,
             'source': 'mount-ra.stl',
             }
    mesh = linkSource(model)
    assert isinstance(mesh, Qt3DRender.QMesh)


def test_linkSource_2(qtbot):
    model = {'parent': None,
             'source': ['sphere', 50, 30, 30],
             }
    mesh = linkSource(model)
    assert isinstance(mesh, Qt3DExtras.QSphereMesh)


def test_linkSource_3(qtbot):
    model = {'parent': None,
             'source': ['cuboid', 50, 30, 30],
             }
    mesh = linkSource(model)
    assert isinstance(mesh, Qt3DExtras.QCuboidMesh)


def test_linkSource_4(qtbot):
    model = {'parent': None,
             'source': ['cylinder', 50, 30, 30, 1],
             }
    mesh = linkSource(model)
    assert isinstance(mesh, Qt3DExtras.QCylinderMesh)


def test_linkSource_5(qtbot):
    model = {'parent': None,
             'source': ['text', 30, 'Arial', 'test'],
             }
    mesh = linkSource(model)
    assert isinstance(mesh, Qt3DExtras.QExtrudedTextMesh)


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
    assert isinstance(trans, Qt3DCore.QTransform)


def test_linkTransform_2(qtbot):
    model = {'parent': None,
             'trans': [1, 1, 1],
             }
    trans = linkTransform(model)
    assert isinstance(trans, Qt3DCore.QTransform)


def test_linkTransform_3(qtbot):
    model = {'parent': None,
             'rot': [1, 1, 1],
             }
    trans = linkTransform(model)
    assert isinstance(trans, Qt3DCore.QTransform)


def test_linkTransform_4(qtbot):
    model = {'parent': None,
             }
    trans = linkTransform(model)
    assert trans is None


def test_linkMaterial_1(qtbot):
    model = {'parent': None,
             'mat': Materials().domeSphere,
             }

    mat = linkMaterial(model)
    assert isinstance(mat, Qt3DExtras.QPhongAlphaMaterial)


def test_linkModel_1(qtbot):
    entityModel = {'root_qt3d': {'entity': Qt3DCore.QEntity()}}

    model = {
        'pointer':
            {'parent': None,
             'source': ['sphere', 50, 30, 30],
             'scale': [1, 1, 1],
             'mat': Materials().pointer,
             }
    }
    linkModel(model, entityModel)


def test_linkModel_2(qtbot):
    entityModel = {'root_qt3d': {'entity': Qt3DCore.QEntity()}}
    model = {
        'pointer':
            {'parent': 'root_qt3d',
             'source': ['sphere', 50, 30, 30],
             'scale': [1, 1, 1],
             'mat': Materials().pointer,
             }
    }
    linkModel(model, entityModel)


def test_getMaterial_1(qtbot):
    entity = None
    val = getMaterial(entity)
    assert val is None


def test_getMaterial_2(qtbot):
    entity = Qt3DCore.QEntity()
    mat = Qt3DExtras.QPhongAlphaMaterial()
    entity.addComponent(mat)
    val = getMaterial(entity)
    assert isinstance(val, Qt3DExtras.QPhongAlphaMaterial)

