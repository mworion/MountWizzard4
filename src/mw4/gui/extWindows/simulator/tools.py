############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from importlib.resources import as_file, files
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor, QFont, QVector3D
from collections.abc import Any


def linkLight(
    node: dict,
) -> Qt3DRender.QPointLight | Qt3DRender.QDirectionalLight | Qt3DRender.QSpotLight | None:
    light = node.get("light")
    if light:
        if light[0] == "point":
            lightSource = Qt3DRender.QPointLight()
            lightSource.setIntensity(light[1])
            lightSource.setColor(QColor(*light[2]))
        elif light[0] == "direction":
            lightSource = Qt3DRender.QDirectionalLight()
            lightSource.setIntensity(light[1])
            lightSource.setColor(QColor(*light[2]))
            lightSource.setWorldDirection(QVector3D(*light[3]))
        elif light[0] == "spot":
            lightSource = Qt3DRender.QSpotLight()
            lightSource.setIntensity(light[1])
            lightSource.setColor(QColor(*light[2]))
            lightSource.setCutOffAngle(light[3])
            lightSource.setLocalDirection(QVector3D(*light[4]))
        else:
            lightSource = None
    else:
        lightSource = None
    return lightSource


def linkSource(
    node: dict,
) -> (
    Qt3DRender.QMesh
    | Qt3DExtras.QCuboidMesh
    | Qt3DExtras.QSphereMesh
    | Qt3DExtras.QCylinderMesh
    | Qt3DExtras.QExtrudedTextMesh
    | None
):
    source = node.get("source")
    if source:
        if isinstance(source, str):
            mesh = Qt3DRender.QMesh()
            sourceFile = files("mw4").joinpath(f"assets/model3D/{source}")
            with as_file(sourceFile) as file:
                mesh.setSource(QUrl.fromLocalFile(file))
            mesh.setMeshName(source)

        elif source[0] == "cuboid":
            mesh = Qt3DExtras.QCuboidMesh()
            mesh.setXExtent(source[1])
            mesh.setYExtent(source[2])
            mesh.setZExtent(source[3])
        elif source[0] == "sphere":
            mesh = Qt3DExtras.QSphereMesh()
            mesh.setRadius(source[1])
            mesh.setRings(source[2])
            mesh.setSlices(source[3])
        elif source[0] == "cylinder":
            mesh = Qt3DExtras.QCylinderMesh()
            mesh.setLength(source[1])
            mesh.setRadius(source[2])
            mesh.setRings(source[3])
            mesh.setSlices(source[4])
        elif source[0] == "text":
            mesh = Qt3DExtras.QExtrudedTextMesh()
            mesh.setDepth(source[1])
            mesh.setFont(QFont())
            mesh.setText(source[3])
        else:
            mesh = None
    else:
        mesh = None

    return mesh


def linkTransform(node: dict) -> Qt3DCore.QTransform | None:
    trans = node.get("trans")
    rot = node.get("rot")
    scale = node.get("scale")

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


def linkMaterial(node: dict) -> Any:
    mat = node.get("mat")
    return mat


def linkModel(model: dict, entityModel: dict) -> None:
    for node in model:
        parent = model[node].get("parent")
        if parent is None:
            continue

        newEntity = Qt3DCore.QEntity(entityModel[parent]["entity"])
        newEntity.setObjectName(node)
        entityModel[node] = {"entity": newEntity}

        mesh = linkSource(model[node])
        if mesh:
            newEntity.addComponent(mesh)
            entityModel[node]["mesh"] = mesh

        transform = linkTransform(model[node])
        if transform:
            newEntity.addComponent(transform)
            entityModel[node]["trans"] = transform

        material = linkMaterial(model[node])
        if material:
            newEntity.addComponent(material)
            entityModel[node]["material"] = material

        light = linkLight(model[node])
        if light:
            newEntity.addComponent(light)
            entityModel[node]["light"] = light


def getMaterial(
    entity: Qt3DCore.QEntity | None,
) -> (
    Qt3DExtras.QMetalRoughMaterial
    | Qt3DExtras.QDiffuseSpecularMaterial
    | Qt3DExtras.QPhongAlphaMaterial
    | Qt3DExtras.QPhongMaterial
    | None
):
    if entity is None:
        return None

    components = entity.components()
    for component in components:
        if isinstance(
            component,
            Qt3DExtras.QMetalRoughMaterial
            | Qt3DExtras.QDiffuseSpecularMaterial
            | Qt3DExtras.QPhongAlphaMaterial
            | Qt3DExtras.QPhongMaterial,
        ):
            return component


def getLight(
    entity: Qt3DCore.QEntity | None,
) -> Qt3DRender.QPointLight | Qt3DRender.QDirectionalLight | Qt3DRender.QSpotLight | None:
    if entity is None:
        return None

    components = entity.components()
    for component in components:
        if isinstance(
            component,
            Qt3DRender.QPointLight | Qt3DRender.QDirectionalLight | Qt3DRender.QSpotLight,
        ):
            return component
