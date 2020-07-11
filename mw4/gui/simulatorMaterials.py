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
from PyQt5.QtGui import QColor
from PyQt5.Qt3DExtras import QDiffuseSpecularMaterial, QMetalRoughMaterial
from PyQt5.Qt3DExtras import QPhongAlphaMaterial, QPhongMaterial

# local import


class Materials():
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
        # self.aluminiumB.setSpecular(QColor(192, 192, 255))

        self.aluminiumR = QDiffuseSpecularMaterial()
        self.aluminiumR.setAmbient(QColor(192, 64, 64))
        self.aluminiumR.setDiffuse(QColor(128, 64, 64))
        # self.aluminiumR.setSpecular(QColor(255, 192, 192))

        self.aluminiumG = QMetalRoughMaterial()
        self.aluminiumG.setBaseColor(QColor(64, 192, 64))
        self.aluminiumG.setMetalness(0.7)
        self.aluminiumG.setRoughness(0.5)

        """
        self.aluminiumG = QDiffuseSpecularMaterial()
        self.aluminiumG.setAmbient(QColor(64, 192, 64))
        self.aluminiumG.setDiffuse(QColor(64, 128, 64))
        # self.aluminiumG.setSpecular(QColor(192, 255, 192))
        """

        self.aluminium = QDiffuseSpecularMaterial()
        self.aluminium.setAmbient(QColor(164, 164, 164))
        self.aluminium.setDiffuse(QColor(164, 164, 164))
        # self.aluminiumG.setSpecular(QColor(192, 255, 192))

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
        self.dome1.setAmbient(QColor(164, 164, 192))
        self.dome1.setDiffuse(QColor(164, 164, 192))
        self.dome1.setSpecular(QColor(164, 164, 192))
        self.dome1.setShininess(0.5)

        self.dome2 = QPhongMaterial()
        self.dome2.setAmbient(QColor(128, 128, 192))
        self.dome2.setDiffuse(QColor(128, 128, 192))
        self.dome2.setSpecular(QColor(128, 128, 192))
        self.dome2.setShininess(0.7)

        self.transparent = QPhongAlphaMaterial()
        self.transparent.setAmbient(QColor(16, 16, 16))
        self.transparent.setDiffuse(QColor(16, 16, 16, 255))
        self.transparent.setSpecular(QColor(16, 16, 16))
        self.transparent.setShininess(0.8)
        self.transparent.setAlpha(0.8)

        self.points = QPhongMaterial()
        self.points.setAmbient(QColor(16, 128, 16))
        self.points.setDiffuse(QColor(16, 128, 16, 255))
        self.points.setSpecular(QColor(16, 128, 16))
        self.points.setShininess(0.9)
        # self.points.setAlpha(0.9)
