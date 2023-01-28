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

# external packages
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QVector3D, QFont
from PyQt5.Qt3DExtras import QCuboidMesh, QSphereMesh
from PyQt5.Qt3DExtras import QExtrudedTextMesh, QCylinderMesh
from PyQt5.Qt3DRender import QMesh
from PyQt5.Qt3DCore import QEntity, QTransform

# local import


def linkSource(currMod):
    """

    :param currMod:
    :return: mesh
    """

    source = currMod.get('source', None)
    if source:
        if isinstance(source, str):
            mesh = QMesh()
            mesh.setSource(QUrl(f'qrc:/model3D/{source}'))
        elif isinstance(source[0], QCuboidMesh):
            mesh = source[0]
            mesh.setXExtent(source[1])
            mesh.setYExtent(source[2])
            mesh.setZExtent(source[3])
        elif isinstance(source[0], QSphereMesh):
            mesh = source[0]
            mesh.setRadius(source[1])
            mesh.setRings(source[2])
            mesh.setSlices(source[3])
        elif isinstance(source[0], QCylinderMesh):
            mesh = source[0]
            mesh.setLength(source[1])
            mesh.setRadius(source[2])
            mesh.setRings(source[3])
            mesh.setSlices(source[4])
        elif isinstance(source[0], QExtrudedTextMesh):
            mesh = source[0]
            mesh.setDepth(source[1])
            mesh.setFont(QFont())
            mesh.setText(source[3])
        else:
            mesh = None
    else:
        mesh = None

    return mesh


def linkTransform(currMod):
    """

    :param currMod:
    :return: transform
    """

    trans = currMod.get('trans', None)
    rot = currMod.get('rot', None)
    scale = currMod.get('scale', None)

    if trans or rot or scale:
        transform = QTransform()

        if trans and isinstance(trans, list) and len(trans) == 3:
            transform.setTranslation(QVector3D(*trans))

        if rot and isinstance(rot, list) and len(rot) == 3:
            transform.setRotationX(rot[0])
            transform.setRotationY(rot[1])
            transform.setRotationZ(rot[2])

        if scale and isinstance(scale, list) and len(scale) == 3:
            transform.setScale3D(QVector3D(*scale))
    else:
        transform = None

    return transform


def linkMaterial(currMod):
    """

    :param currMod:
    :return: material
    """

    mat = currMod.get('mat', None)
    return mat


def linkModel(model, name, rEntity):
    """

    :param model:
    :param name:
    :param rEntity:
    :return: true for test purpose
    """

    currMod = model[name]

    parent = currMod.get('parent', None)
    if parent and model.get(parent, None):
        currMod['e'] = QEntity(model[parent]['e'])
    else:
        currMod['e'] = QEntity(rEntity)

    mesh = linkSource(currMod)
    if mesh:
        currMod['e'].addComponent(mesh)
        currMod['m'] = mesh

    transform = linkTransform(currMod)
    if transform:
        currMod['e'].addComponent(transform)
        currMod['t'] = transform

    material = linkMaterial(currMod)
    if material:
        currMod['mat'] = material
        currMod['e'].addComponent(material)

    return True
