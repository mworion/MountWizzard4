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

# external packages
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QColor, QVector3D, QFont
from PyQt5.Qt3DExtras import QDiffuseSpecularMaterial, QMetalRoughMaterial, QTextureMaterial
from PyQt5.Qt3DExtras import QPhongAlphaMaterial, QPhongMaterial
from PyQt5.Qt3DExtras import QCuboidMesh, QSphereMesh
from PyQt5.Qt3DExtras import QExtrudedTextMesh, QCylinderMesh
from PyQt5.Qt3DRender import QTextureLoader, QMesh
from PyQt5.Qt3DCore import QEntity, QTransform

# local import
from mw4.gui.widget import MWidget


@staticmethod
def linkModel(model, name, rootEntity):
    """

    :param model:
    :param name:
    :param rootEntity:
    :return:
    """

    currMod = model[name]

    parent = currMod.get('parent', None)
    if parent and model.get(parent, None):
        currMod['e'] = QEntity(model[parent]['e'])
    else:
        currMod['e'] = QEntity(rootEntity)

    visible = currMod.get('visible', True)
    currMod['e'].setEnabled(visible)

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

        currMod['e'].addComponent(mesh)
        currMod['m'] = mesh

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

        currMod['e'].addComponent(transform)
        currMod['t'] = transform

    mat = currMod.get('mat', None)
    if mat:
        currMod['mat'] = mat
        currMod['e'].addComponent(mat)


class Materials(MWidget):
    def __init__(self):
        self.aluminiumS = QMetalRoughMaterial()
        self.aluminiumS.setBaseColor(QColor(127, 127, 127))
        self.aluminiumS.setMetalness(0.7)
        self.aluminiumS.setRoughness(0.5)

        self.aluminiumGrey = QMetalRoughMaterial()
        self.aluminiumGrey.setBaseColor(QColor(164, 164, 192))
        self.aluminiumGrey.setMetalness(0.3)
        self.aluminiumGrey.setRoughness(0.5)

        self.aluminiumB = QDiffuseSpecularMaterial()
        self.aluminiumB.setAmbient(QColor(64, 64, 128))
        self.aluminiumB.setDiffuse(QColor(64, 64, 128))

        self.aluminiumR = QDiffuseSpecularMaterial()
        self.aluminiumR.setAmbient(QColor(192, 64, 64))
        self.aluminiumR.setDiffuse(QColor(192, 64, 64))

        self.environ1 = QMetalRoughMaterial()
        self.environ1.setBaseColor(QColor(192, 164, 64))
        self.environ1.setMetalness(0.5)
        self.environ1.setRoughness(1)

        self.aluminium = QDiffuseSpecularMaterial()
        self.aluminium.setAmbient(QColor(164, 164, 164))
        self.aluminium.setDiffuse(QColor(164, 164, 164))

        self.white = QDiffuseSpecularMaterial()
        self.white.setAmbient(QColor(228, 228, 228))
        self.white.setShininess(0.7)

        self.glass = QDiffuseSpecularMaterial()
        self.glass.setAlphaBlendingEnabled(True)
        self.glass.setAmbient(QColor(0, 0, 112))
        self.glass.setDiffuse(QColor(128, 128, 192, 220))

        self.stainless = QDiffuseSpecularMaterial()
        self.stainless.setAmbient(QColor(224, 223, 219))
        self.stainless.setDiffuse(QColor(145, 148, 152))
        self.stainless.setSpecular(QColor(255, 255, 230))
        self.stainless.setShininess(0.9)

        self.dome1 = QPhongMaterial()
        self.dome1.setAmbient(self.COLOR_ASTRO)
        self.dome1.setDiffuse(self.COLOR_ASTRO)
        self.dome1.setSpecular(self.COLOR_ASTRO)
        self.dome1.setShininess(0.5)

        self.dome2 = QPhongMaterial()
        self.dome2.setAmbient(QColor(24, 108, 124))
        self.dome2.setDiffuse(QColor(24, 108, 124))
        self.dome2.setSpecular(QColor(24, 108, 124))
        self.dome2.setShininess(0.7)

        self.dome3 = QPhongMaterial()
        self.dome3.setAmbient(QColor(16, 72, 96))
        self.dome3.setDiffuse(QColor(16, 72, 96))
        self.dome3.setSpecular(QColor(16, 72, 96))
        self.dome3.setShininess(0.3)

        self.dome1t = QPhongAlphaMaterial()
        self.dome1t.setAmbient(QColor(16, 72, 96))
        self.dome1t.setDiffuse(QColor(16, 72, 96))
        self.dome1t.setSpecular(QColor(16, 72, 96))
        self.dome1t.setShininess(0.5)
        self.dome1t.setAlpha(0.8)

        self.dome2t = QPhongAlphaMaterial()
        self.dome2t.setAmbient(QColor(12, 54, 72))
        self.dome2t.setDiffuse(QColor(12, 54, 72))
        self.dome2t.setSpecular(QColor(12, 54, 72))
        self.dome2t.setShininess(0.7)
        self.dome2t.setAlpha(0.8)

        self.dome3t = QPhongAlphaMaterial()
        self.dome3t.setAmbient(QColor(8, 36, 48))
        self.dome3t.setDiffuse(QColor(8, 36, 48))
        self.dome3t.setSpecular(QColor(8, 36, 48))
        self.dome3t.setShininess(0.3)
        self.dome3t.setAlpha(0.8)

        self.points = QPhongMaterial()
        self.points.setAmbient(QColor(16, 128, 16))
        self.points.setDiffuse(QColor(16, 128, 16))
        self.points.setSpecular(QColor(16, 128, 16))
        self.points.setShininess(1)

        self.lines = QPhongMaterial()
        self.lines.setAmbient(QColor(96, 96, 0))
        self.lines.setDiffuse(QColor(96, 96, 0))
        self.lines.setSpecular(QColor(96, 96, 0))
        self.lines.setShininess(1.0)

        self.numbers = QPhongMaterial()
        self.numbers.setAmbient(QColor(16, 192, 16))
        self.numbers.setDiffuse(QColor(16, 192, 16))
        self.numbers.setSpecular(QColor(16, 192, 16))
        self.numbers.setShininess(1)

        self.pointer = QPhongMaterial()
        self.pointer.setAmbient(self.COLOR_PINK)
        self.pointer.setDiffuse(self.COLOR_PINK)
        self.pointer.setSpecular(self.COLOR_PINK)
        self.pointer.setShininess(1)

        self.walls = QPhongAlphaMaterial()
        self.walls.setAmbient(QColor(96, 82, 32))
        self.walls.setDiffuse(QColor(96, 82, 32))
        self.walls.setSpecular(QColor(96, 82, 32))
        self.walls.setShininess(0.3)
        self.walls.setAlpha(0.5)

        self.mw4 = QTextureMaterial()
        self.texture = QTextureLoader()
        self.texture.setMirrored(False)
        self.texture.setSource(QUrl(':/icon/mw4.png'))
        self.mw4.setTexture(self.texture)
