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
from PySide6.QtGui import QColor
from PySide6.Qt3DExtras import Qt3DExtras

# local import
from gui.utilities.stylesQtCss import Styles


class Materials(Styles):

    __all__ = ['Materials']

    """
    class Materials defines all used materials for the loaded stl models or the
    meshed build programmatically inside the simulator
    """

    def __init__(self):
        super().__init__()

        self.mountBlack = Qt3DExtras.QMetalRoughMaterial()
        self.mountBlack.setBaseColor(QColor(127, 127, 127))
        self.mountBlack.setAmbientOcclusion(0)
        self.mountBlack.setMetalness(0.7)
        self.mountBlack.setRoughness(0.5)

        self.aluminiumGrey = Qt3DExtras.QMetalRoughMaterial()
        self.aluminiumGrey.setBaseColor(QColor(164, 164, 192))
        self.aluminiumGrey.setAmbientOcclusion(0)
        self.aluminiumGrey.setMetalness(0.3)
        self.aluminiumGrey.setRoughness(0.5)

        self.environ = Qt3DExtras.QMetalRoughMaterial()
        self.environ.setBaseColor(QColor(self.M_BLUE2))
        self.environ.setAmbientOcclusion(0.0)
        self.environ.setMetalness(0.1)
        self.environ.setRoughness(0.0)

        self.stainless = Qt3DExtras.QMetalRoughMaterial()
        self.stainless.setBaseColor(QColor(255, 255, 255))
        self.stainless.setAmbientOcclusion(0)
        self.stainless.setMetalness(1)
        self.stainless.setRoughness(0.2)

        self.domeColumn = Qt3DExtras.QMetalRoughMaterial()
        self.domeColumn.setBaseColor(QColor(196, 196, 196))
        self.domeColumn.setAmbientOcclusion(0)
        self.domeColumn.setMetalness(0.3)
        self.domeColumn.setRoughness(0.5)

        self.aluCCD = Qt3DExtras.QDiffuseSpecularMaterial()
        self.aluCCD.setAmbient(QColor(32, 32, 92))
        self.aluCCD.setSpecular(QColor(64, 64, 255))
        self.aluCCD.setDiffuse(QColor(32, 32, 92, 255))
        self.aluCCD.setAlphaBlendingEnabled(False)

        self.aluRed = Qt3DExtras.QDiffuseSpecularMaterial()
        self.aluRed.setAmbient(QColor(96, 32, 32))
        self.aluRed.setSpecular(QColor(255, 64, 64))
        self.aluRed.setDiffuse(QColor(96, 32, 32, 255))
        self.aluRed.setAlphaBlendingEnabled(False)
        self.aluRed.setShininess(128)

        self.aluKnobs = Qt3DExtras.QDiffuseSpecularMaterial()
        self.aluKnobs.setAmbient(QColor(128, 128, 128))
        self.aluKnobs.setSpecular(QColor(255, 255, 255))
        self.aluKnobs.setDiffuse(QColor(128, 128, 128, 255))
        self.aluKnobs.setShininess(128)
        self.aluKnobs.setAlphaBlendingEnabled(False)

        self.white = Qt3DExtras.QDiffuseSpecularMaterial()
        self.white.setAmbient(QColor(224, 224, 224))
        self.white.setSpecular(QColor(224, 224, 224))
        self.white.setDiffuse(QColor(224, 224, 224, 255))
        self.white.setAlphaBlendingEnabled(False)
        self.white.setShininess(128)

        self.glass = Qt3DExtras.QDiffuseSpecularMaterial()
        self.glass.setAmbient(QColor(0, 0, 112))
        self.glass.setSpecular(QColor(0, 0, 112))
        self.glass.setDiffuse(QColor(128, 128, 192, 64))
        self.glass.setAlphaBlendingEnabled(True)
        self.glass.setShininess(128)

        """
        self.stainless = Qt3DExtras.QDiffuseSpecularMaterial()
        self.stainless.setAmbient(QColor(192, 192, 192))
        self.stainless.setDiffuse(QColor(128, 128, 128))
        self.stainless.setSpecular(QColor(255, 255, 255, 255))
        self.stainless.setAlphaBlendingEnabled(False)
        self.stainless.setShininess(255)
        """

        self.domeSphere = Qt3DExtras.QPhongAlphaMaterial()
        self.domeSphere.setAmbient(QColor(self.M_BLUE2))
        self.domeSphere.setDiffuse(QColor(self.M_BLUE2))
        self.domeSphere.setSpecular(QColor(self.M_BLUE2))
        self.domeSphere.setShininess(64)
        self.domeSphere.setAlpha(1)

        self.domeSlit = Qt3DExtras.QPhongAlphaMaterial()
        self.domeSlit.setAmbient(QColor(self.M_BLUE3))
        self.domeSlit.setDiffuse(QColor(self.M_BLUE3))
        self.domeSlit.setSpecular(QColor(self.M_BLUE3))
        self.domeSlit.setShininess(64)
        self.domeSlit.setAlpha(1)

        self.domeDoor = Qt3DExtras.QPhongAlphaMaterial()
        self.domeDoor.setAmbient(QColor(self.M_BLUE3))
        self.domeDoor.setDiffuse(QColor(self.M_BLUE3))
        self.domeDoor.setSpecular(QColor(self.M_BLUE3))
        self.domeDoor.setShininess(64)
        self.domeDoor.setAlpha(1)

        self.pointsActive = Qt3DExtras.QPhongMaterial()
        self.pointsActive.setAmbient(QColor(self.M_GREEN))
        self.pointsActive.setDiffuse(QColor(self.M_BLUE1))
        self.pointsActive.setSpecular(QColor(self.M_BLUE1))
        self.pointsActive.setShininess(64)

        self.points = Qt3DExtras.QPhongMaterial()
        self.points.setAmbient(QColor(self.M_YELLOW))
        self.points.setDiffuse(QColor(self.M_GREY1))
        self.points.setSpecular(QColor(self.M_GREY1))
        self.points.setShininess(64)

        self.lines = Qt3DExtras.QPhongMaterial()
        self.lines.setAmbient(QColor(self.M_GREY1))
        self.lines.setDiffuse(QColor(self.M_GREY1))
        self.lines.setSpecular(QColor(self.M_GREY1))
        self.lines.setShininess(64)

        self.numbers = Qt3DExtras.QPhongMaterial()
        self.numbers.setAmbient(QColor(self.M_YELLOW))
        self.numbers.setDiffuse(QColor(self.M_YELLOW))
        self.numbers.setSpecular(QColor(self.M_YELLOW))
        self.numbers.setShininess(255)

        self.numbersActive = Qt3DExtras.QPhongMaterial()
        self.numbersActive.setAmbient(QColor(self.M_GREEN))
        self.numbersActive.setDiffuse(QColor(self.M_GREEN))
        self.numbersActive.setSpecular(QColor(self.M_GREEN))
        self.numbersActive.setShininess(255)

        self.pointer = Qt3DExtras.QPhongMaterial()
        self.pointer.setAmbient(QColor(self.M_PINK1))
        self.pointer.setDiffuse(QColor(self.M_PINK1))
        self.pointer.setSpecular(QColor(self.M_PINK1))
        self.pointer.setShininess(255)

        self.laser = Qt3DExtras.QPhongMaterial()
        self.laser.setAmbient(QColor(self.M_YELLOW))
        self.laser.setDiffuse(QColor(self.M_YELLOW))
        self.laser.setSpecular(QColor(self.M_YELLOW))
        self.laser.setShininess(255)

        self.walls = Qt3DExtras.QPhongAlphaMaterial()
        self.walls.setAmbient(QColor(self.M_GREY1))
        self.walls.setDiffuse(QColor(self.M_GREY1))
        self.walls.setSpecular(QColor(self.M_GREY1))
        self.walls.setAlpha(1)
        self.walls.setShininess(64)

        self.horizon = Qt3DExtras.QPhongAlphaMaterial()
        self.horizon.setAmbient(QColor(self.M_BLUE4))
        self.horizon.setDiffuse(QColor(self.M_YELLOW))
        self.horizon.setSpecular(QColor(self.M_YELLOW))
        self.horizon.setAlpha(0.35)
        self.horizon.setShininess(64)
