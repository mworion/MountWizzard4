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
from PySide6.QtCore import QUrl
from PySide6.QtGui import QVector3D, QFont
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DCore import Qt3DCore

# local import


def linkLight(node):
    """
    :param node:
    :return:
    """
    light = node.get('light')
    if light:
        if isinstance(light[0], Qt3DRender.QPointLight):
            lightSource = light[0]
            lightSource.setIntensity(light[1])
            lightSource.setColor(light[2])
        elif isinstance(light[0], Qt3DRender.QDirectionalLight):
            lightSource = light[0]
            lightSource.setIntensity(light[1])
            lightSource.setColor(light[2])
            lightSource.setWorldDirection(light[3])
        elif isinstance(light[0], Qt3DRender.QSpotLight):
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
            mesh = Qt3DRender.QMesh()
            mesh.setSource(QUrl(f'qrc:/model3D/{source}'))
            mesh.sourceChanged.connect(lambda: print(f'{mesh.meshName}: {mesh.status}'))

        elif isinstance(source[0], Qt3DExtras.QCuboidMesh):
            mesh = source[0]
            mesh.setXExtent(source[1])
            mesh.setYExtent(source[2])
            mesh.setZExtent(source[3])
        elif isinstance(source[0], Qt3DExtras.QSphereMesh):
            mesh = source[0]
            mesh.setRadius(source[1])
            mesh.setRings(source[2])
            mesh.setSlices(source[3])
        elif isinstance(source[0], Qt3DExtras.QCylinderMesh):
            mesh = source[0]
            mesh.setLength(source[1])
            mesh.setRadius(source[2])
            mesh.setRings(source[3])
            mesh.setSlices(source[4])
        elif isinstance(source[0], Qt3DExtras.QExtrudedTextMesh):
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
        transform = Qt3DCore.QTransform()

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

        newEntity = Qt3DCore.QEntity()
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
        if isinstance(component, Qt3DCore.QTransform):
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
        if isinstance(component, (Qt3DExtras.QMetalRoughMaterial,
                                  Qt3DExtras.QDiffuseSpecularMaterial,
                                  Qt3DExtras.QPhongAlphaMaterial,
                                  Qt3DExtras.QPhongMaterial)):
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
        if isinstance(component, (Qt3DExtras.QCuboidMesh,
                                  Qt3DExtras.QSphereMesh,
                                  Qt3DExtras.QExtrudedTextMesh,
                                  Qt3DExtras.QCylinderMesh)):
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
        if isinstance(component, (Qt3DRender.QPointLight,
                                  Qt3DRender.QDirectionalLight,
                                  Qt3DRender.QSpotLight)):
            return component
