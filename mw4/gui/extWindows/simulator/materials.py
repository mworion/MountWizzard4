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
from PyQt6.QtGui import QColor
from PyQt6.Qt3DExtras import QDiffuseSpecularMaterial, QMetalRoughMaterial
from PyQt6.Qt3DExtras import QPhongAlphaMaterial, QPhongMaterial

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
        self.aluminiumR.setAmbient(QColor(255, 64, 64))
        self.aluminiumR.setDiffuse(QColor(255, 64, 64))

        self.environ1 = QDiffuseSpecularMaterial()
        self.environ1.setAmbient(QColor(self.M_BLUE4))
        self.environ1.setDiffuse(QColor(self.M_BLUE4))
        self.environ1.setShininess(1)
        self.environ1.setSpecular(1)

        self.aluminium = QDiffuseSpecularMaterial()
        self.aluminium.setAmbient(QColor(164, 164, 164))
        self.aluminium.setDiffuse(QColor(164, 164, 164))

        self.white = QDiffuseSpecularMaterial()
        self.white.setAmbient(QColor(224, 224, 224))
        self.white.setShininess(128)

        self.glass = QDiffuseSpecularMaterial()
        self.glass.setAlphaBlendingEnabled(True)
        self.glass.setAmbient(QColor(0, 0, 112))
        self.glass.setDiffuse(QColor(128, 128, 192, 220))

        self.stainless = QDiffuseSpecularMaterial()
        self.stainless.setAmbient(QColor(224, 223, 219))
        self.stainless.setDiffuse(QColor(145, 148, 152))
        self.stainless.setSpecular(QColor(255, 255, 230))
        self.stainless.setShininess(255)

        self.dome1 = QPhongAlphaMaterial()
        self.dome1.setAmbient(QColor(self.M_BLUE2))
        self.dome1.setDiffuse(QColor(self.M_BLUE2))
        self.dome1.setSpecular(QColor(self.M_BLUE2))
        self.dome1.setShininess(64)
        self.dome1.setAlpha(1)

        self.dome2 = QPhongAlphaMaterial()
        self.dome2.setAmbient(QColor(self.M_BLUE3))
        self.dome2.setDiffuse(QColor(self.M_BLUE3))
        self.dome2.setSpecular(QColor(self.M_BLUE3))
        self.dome2.setShininess(64)
        self.dome2.setAlpha(1)

        self.pointsActive = QPhongMaterial()
        self.pointsActive.setAmbient(QColor(self.M_GREEN))
        self.pointsActive.setDiffuse(QColor(self.M_BLUE1))
        self.pointsActive.setSpecular(QColor(self.M_BLUE1))
        self.pointsActive.setShininess(64)

        self.points = QPhongMaterial()
        self.points.setAmbient(QColor(self.M_YELLOW))
        self.points.setDiffuse(QColor(self.M_GREY1))
        self.points.setSpecular(QColor(self.M_GREY1))
        self.points.setShininess(64)

        self.lines = QPhongMaterial()
        self.lines.setAmbient(QColor(self.M_GREY1))
        self.lines.setDiffuse(QColor(self.M_GREY1))
        self.lines.setSpecular(QColor(self.M_GREY1))
        self.lines.setShininess(64)

        self.numbers = QPhongMaterial()
        self.numbers.setAmbient(QColor(self.M_YELLOW))
        self.numbers.setDiffuse(QColor(self.M_YELLOW))
        self.numbers.setSpecular(QColor(self.M_YELLOW))
        self.numbers.setShininess(255)

        self.numbersActive = QPhongMaterial()
        self.numbersActive.setAmbient(QColor(self.M_GREEN))
        self.numbersActive.setDiffuse(QColor(self.M_GREEN))
        self.numbersActive.setSpecular(QColor(self.M_GREEN))
        self.numbersActive.setShininess(255)

        self.pointer = QPhongMaterial()
        self.pointer.setAmbient(QColor(self.M_PINK1))
        self.pointer.setDiffuse(QColor(self.M_PINK1))
        self.pointer.setSpecular(QColor(self.M_PINK1))
        self.pointer.setShininess(255)

        self.laser = QPhongMaterial()
        self.laser.setAmbient(QColor(self.M_YELLOW))
        self.laser.setDiffuse(QColor(self.M_YELLOW))
        self.laser.setSpecular(QColor(self.M_YELLOW))
        self.laser.setShininess(255)

        self.walls = QPhongAlphaMaterial()
        self.walls.setAmbient(QColor(self.M_GREY1))
        self.walls.setDiffuse(QColor(self.M_GREY1))
        self.walls.setSpecular(QColor(self.M_GREY1))
        self.walls.setAlpha(1)
        self.walls.setShininess(64)

        self.horizon = QPhongAlphaMaterial()
        self.horizon.setAmbient(QColor(self.M_BLUE4))
        self.horizon.setDiffuse(QColor(self.M_YELLOW))
        self.walls.setSpecular(QColor(self.M_YELLOW))
        self.horizon.setAlpha(0.35)
        self.horizon.setShininess(64)
