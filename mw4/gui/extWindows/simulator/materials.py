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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtGui import QColor
from PyQt5.Qt3DExtras import QDiffuseSpecularMaterial, QMetalRoughMaterial
from PyQt5.Qt3DExtras import QPhongAlphaMaterial, QPhongMaterial

# local import
from gui.utilities.stylesQtCss import Styles


class Materials(Styles):

    __all__ = ['Materials',
               ]

    """
    class Materials defines all used materials for the loaded stl models or the meshed build
    programmatically inside the simulator
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
        self.aluminiumR.setAmbient(QColor(192, 64, 64))
        self.aluminiumR.setDiffuse(QColor(192, 64, 64))

        self.environ1 = QDiffuseSpecularMaterial()
        self.environ1.setAmbient(QColor(0, 0, 64))
        self.environ1.setDiffuse(QColor(24, 60, 0))
        # self.environ1.setSpecular(QColor(64, 164, 0))
        self.environ1.setShininess(50)

        self.aluminium = QDiffuseSpecularMaterial()
        self.aluminium.setAmbient(QColor(164, 164, 164))
        self.aluminium.setDiffuse(QColor(164, 164, 164))

        self.white = QDiffuseSpecularMaterial()
        self.white.setAmbient(QColor(228, 228, 228))
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

        self.dome1 = QPhongMaterial()
        self.dome1.setAmbient(self.COLOR_ASTRO)
        self.dome1.setDiffuse(self.COLOR_ASTRO)
        self.dome1.setSpecular(self.COLOR_ASTRO)
        self.dome1.setShininess(64)

        self.dome2 = QPhongMaterial()
        self.dome2.setAmbient(QColor(24, 108, 124))
        self.dome2.setDiffuse(QColor(24, 108, 124))
        self.dome2.setSpecular(QColor(24, 108, 124))
        self.dome2.setShininess(64)

        self.dome3 = QPhongMaterial()
        self.dome3.setAmbient(QColor(16, 72, 96))
        self.dome3.setDiffuse(QColor(16, 72, 96))
        self.dome3.setSpecular(QColor(16, 72, 96))
        self.dome3.setShininess(64)

        self.dome1t = QPhongAlphaMaterial()
        self.dome1t.setAmbient(QColor(16, 72, 96))
        self.dome1t.setDiffuse(QColor(16, 72, 96))
        self.dome1t.setSpecular(QColor(16, 72, 96))
        self.dome1t.setShininess(64)
        self.dome1t.setAlpha(0.5)

        self.dome2t = QPhongAlphaMaterial()
        self.dome2t.setAmbient(QColor(12, 54, 72))
        self.dome2t.setDiffuse(QColor(12, 54, 72))
        self.dome2t.setSpecular(QColor(12, 54, 72))
        self.dome2t.setShininess(64)
        self.dome2t.setAlpha(0.5)

        self.dome3t = QPhongAlphaMaterial()
        self.dome3t.setAmbient(QColor(8, 36, 48))
        self.dome3t.setDiffuse(QColor(8, 36, 48))
        self.dome3t.setSpecular(QColor(8, 36, 48))
        self.dome3t.setShininess(64)
        self.dome3t.setAlpha(0.5)

        self.pointsActive = QPhongMaterial()
        self.pointsActive.setAmbient(QColor(16, 128, 16))
        self.pointsActive.setDiffuse(QColor(16, 128, 16))
        self.pointsActive.setSpecular(QColor(16, 128, 16))
        self.pointsActive.setShininess(255)

        self.points = QPhongMaterial()
        self.points.setAmbient(QColor(128, 128, 16))
        self.points.setDiffuse(QColor(128, 128, 16))
        self.points.setSpecular(QColor(128, 128, 16))
        self.points.setShininess(255)

        self.lines = QPhongMaterial()
        self.lines.setAmbient(QColor(92, 92, 92))
        self.lines.setDiffuse(QColor(92, 92, 92))
        self.lines.setSpecular(QColor(92, 92, 92))
        self.lines.setShininess(255)

        self.numbers = QPhongMaterial()
        self.numbers.setAmbient(QColor(192, 192, 16))
        self.numbers.setDiffuse(QColor(192, 192, 16))
        self.numbers.setSpecular(QColor(192, 192, 16))
        self.numbers.setShininess(255)

        self.numbersActive = QPhongMaterial()
        self.numbersActive.setAmbient(QColor(16, 192, 16))
        self.numbersActive.setDiffuse(QColor(16, 192, 16))
        self.numbersActive.setSpecular(QColor(16, 192, 16))
        self.numbersActive.setShininess(255)

        self.pointer = QPhongMaterial()
        self.pointer.setAmbient(self.COLOR_PINK)
        self.pointer.setDiffuse(self.COLOR_PINK)
        self.pointer.setSpecular(self.COLOR_PINK)
        self.pointer.setShininess(255)

        self.laser = QPhongMaterial()
        self.laser.setAmbient(QColor(255, 192, 0))
        self.laser.setDiffuse(QColor(255, 192, 0))
        self.laser.setSpecular(QColor(255, 192, 0))
        self.laser.setShininess(255)

        self.walls = QPhongMaterial()
        self.walls.setAmbient(QColor(100, 10, 65))
        self.walls.setDiffuse(QColor(100, 10, 65))
        self.walls.setSpecular(QColor(100, 10, 65))
        self.walls.setShininess(255)
