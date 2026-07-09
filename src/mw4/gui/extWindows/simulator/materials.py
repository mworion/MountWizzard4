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
from mw4.gui.styles.styles import Styles
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtGui import QColor


class Materials(Styles):
    """
    class Materials defines all used materials for the loaded stl models or the
    meshed build programmatically inside the simulator
    """

    def __init__(self):
        super().__init__()

        self.mountBlack = Qt3DExtras.QMetalRoughMaterial()
        self.mountBlack.setBaseColor(QColor(127, 127, 127))
        self.mountBlack.setMetalness(0.8)
        self.mountBlack.setRoughness(0.5)

        self.aluminiumGrey = Qt3DExtras.QMetalRoughMaterial()
        self.aluminiumGrey.setBaseColor(QColor(164, 164, 192))
        self.aluminiumGrey.setMetalness(0.3)
        self.aluminiumGrey.setRoughness(0.5)

        self.environ = Qt3DExtras.QMetalRoughMaterial()
        self.environ.setBaseColor(self.M_PRIM2)
        self.environ.setMetalness(0.5)
        self.environ.setRoughness(0.5)

        self.stainless = Qt3DExtras.QMetalRoughMaterial()
        self.stainless.setBaseColor(QColor(255, 255, 255))
        self.stainless.setMetalness(0.9)
        self.stainless.setRoughness(0.8)

        self.domeColumn = Qt3DExtras.QMetalRoughMaterial()
        self.domeColumn.setBaseColor(QColor(150, 90, 50))
        self.domeColumn.setMetalness(0)
        self.domeColumn.setRoughness(1)

        self.aluCCD = Qt3DExtras.QDiffuseSpecularMaterial()
        self.aluCCD.setAmbient(QColor(32, 32, 92))
        self.aluCCD.setSpecular(QColor(64, 64, 255))
        self.aluCCD.setDiffuse(QColor(32, 32, 92, 255))
        self.aluCCD.setAlphaBlendingEnabled(False)

        self.aluRed = Qt3DExtras.QDiffuseSpecularMaterial()
        self.aluRed.setAmbient(QColor(128, 32, 32))
        self.aluRed.setSpecular(QColor(255, 255, 255))
        self.aluRed.setDiffuse(QColor(128, 32, 32, 255))
        self.aluRed.setAlphaBlendingEnabled(False)
        self.aluRed.setShininess(200)

        self.aluKnobs = Qt3DExtras.QDiffuseSpecularMaterial()
        self.aluKnobs.setAmbient(QColor(128, 128, 128))
        self.aluKnobs.setSpecular(QColor(255, 255, 255))
        self.aluKnobs.setDiffuse(QColor(64, 64, 64, 255))
        self.aluKnobs.setShininess(64)
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
        self.domeSphere.setAmbient(self.M_PRIM2)
        self.domeSphere.setDiffuse(self.M_PRIM2)
        self.domeSphere.setSpecular(self.M_PRIM2)
        self.domeSphere.setShininess(64)
        self.domeSphere.setAlpha(1)

        self.domeSlit = Qt3DExtras.QPhongAlphaMaterial()
        self.domeSlit.setAmbient(self.M_PRIM3)
        self.domeSlit.setDiffuse(self.M_PRIM3)
        self.domeSlit.setSpecular(self.M_PRIM3)
        self.domeSlit.setShininess(64)
        self.domeSlit.setAlpha(1)

        self.domeDoor = Qt3DExtras.QPhongAlphaMaterial()
        self.domeDoor.setAmbient(self.M_PRIM3)
        self.domeDoor.setDiffuse(self.M_PRIM3)
        self.domeDoor.setSpecular(self.M_PRIM3)
        self.domeDoor.setShininess(64)
        self.domeDoor.setAlpha(1)

        self.pointsRed = Qt3DExtras.QPhongMaterial()
        self.pointsRed.setAmbient(self.M_RED)
        self.pointsRed.setDiffuse(self.M_RED)
        self.pointsRed.setSpecular(self.M_RED)
        self.pointsRed.setShininess(64)

        self.pointsGreen = Qt3DExtras.QPhongMaterial()
        self.pointsGreen.setAmbient(self.M_GREEN)
        self.pointsGreen.setDiffuse(self.M_GREEN)
        self.pointsGreen.setSpecular(self.M_GREEN)
        self.pointsGreen.setShininess(64)

        self.points = Qt3DExtras.QPhongMaterial()
        self.points.setAmbient(self.M_TER)
        self.points.setDiffuse(self.M_TER)
        self.points.setSpecular(128)

        self.lines = Qt3DExtras.QPhongMaterial()
        self.lines.setAmbient(self.M_GRAY)
        self.lines.setDiffuse(self.M_GRAY)
        self.lines.setSpecular(self.M_GRAY)
        self.lines.setShininess(0)

        self.pointer = Qt3DExtras.QPhongMaterial()
        self.pointer.setAmbient(self.M_PINK1)
        self.pointer.setDiffuse(self.M_PINK1)
        self.pointer.setSpecular(self.M_PINK1)
        self.pointer.setShininess(255)

        self.laser = Qt3DExtras.QPhongMaterial()
        self.laser.setAmbient(self.M_YELLOW)
        self.laser.setDiffuse(self.M_YELLOW)
        self.laser.setSpecular(self.M_YELLOW)
        self.laser.setShininess(255)

        self.walls = Qt3DExtras.QPhongAlphaMaterial()
        self.walls.setAmbient(self.M_SEC1)
        self.walls.setDiffuse(self.M_SEC1)
        self.walls.setSpecular(self.M_SEC1)
        self.walls.setAlpha(1)
        self.walls.setShininess(64)

        self.horizon = Qt3DExtras.QPhongAlphaMaterial()
        self.horizon.setAmbient(self.M_PRIM4)
        self.horizon.setDiffuse(self.M_YELLOW)
        self.horizon.setSpecular(self.M_YELLOW)
        self.horizon.setAlpha(0.35)
        self.horizon.setShininess(64)
