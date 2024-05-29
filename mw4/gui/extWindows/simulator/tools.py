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

# external packages
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QVector3D, QFont
from PyQt6.Qt3DExtras import QCuboidMesh, QSphereMesh
from PyQt6.Qt3DExtras import QExtrudedTextMesh, QCylinderMesh
from PyQt6.Qt3DExtras import QPhongAlphaMaterial
from PyQt6.Qt3DRender import QMesh
from PyQt6.Qt3DRender import QPointLight, QDirectionalLight, QSpotLight
from PyQt6.Qt3DCore import QEntity, QTransform

# local import


def linkLight(node):
    """
    :param node:
    :return:
    """
    light = node.get('light')
    if light:
        if isinstance(light[0], QPointLight):
            lightSource = light[0]
            lightSource.setIntensity(light[1])
            lightSource.setColor(light[2])
        elif isinstance(light[0], QDirectionalLight):
            lightSource = light[0]
            lightSource.setIntensity(light[1])
            lightSource.setColor(light[2])
            lightSource.setWorldDirection(light[3])
        elif isinstance(light[0], QSpotLight):
            lightSource = light[0]
            lightSource.setIntensity(light[1])
            lightSource.setColor(light[2])
            lightSource.setCutOffAngle(light[3])
            lightSource.setLocalDirection(light[4])
        else:
            lightSource = None
    else:
        lightSource = None

    return lightSource


def linkSource(node):
    """
    :param node:
    :return: mesh
    """
    source = node.get('source')
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


def linkTransform(node):
    """
    :param node:
    :return: transform
    """
    trans = node.get('trans')
    rot = node.get('rot')
    scale = node.get('scale')

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


def linkMaterial(node):
    """
    :param node:
    :return: material
    """
    mat = node.get('mat')
    return mat


def linkModel(model, entityModel):
    """
    :param model:
    :param entityModel:
    :return: true for test purpose
    """
    for node in model:
        parent = model[node].get('parent')
        if parent is None:
            continue

        newEntity = QEntity()
        newEntity.setParent(entityModel[parent])
        entityModel[node] = newEntity

        mesh = linkSource(model[node])
        if mesh:
            newEntity.addComponent(mesh)

        transform = linkTransform(model[node])
        if transform:
            newEntity.addComponent(transform)

        material = linkMaterial(model[node])
        if material:
            newEntity.addComponent(material)

        light = linkLight(model[node])
        if light:
            newEntity.addComponent(light)


def getTransformation(entity):
    """
    :param entity:
    :return:
    """
    if entity is None:
        return None
    components = entity.components()
    for component in components:
        if isinstance(component, QTransform):
            return component


def getMaterial(entity):
    """
    :param entity:
    :return:
    """
    if entity is None:
        return None
    components = entity.components()
    for component in components:
        if isinstance(component, (QPhongAlphaMaterial)):
            return component


def getMesh(entity):
    """
    :param entity:
    :return:
    """
    if entity is None:
        return None
    components = entity.components()
    for component in components:
        if isinstance(component, (QCuboidMesh, QSphereMesh,
                                  QExtrudedTextMesh, QCylinderMesh)):
            return component


def getLight(entity):
    """
    :param entity:
    :return:
    """
    if entity is None:
        return None
    components = entity.components()
    for component in components:
        if isinstance(component, (QPointLight, QDirectionalLight,
                                  QSpotLight)):
            return component
