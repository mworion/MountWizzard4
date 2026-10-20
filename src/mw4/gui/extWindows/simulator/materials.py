# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.gui.styles.styles import Styles
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtGui import QColor

RGBA = tuple[int, ...]


class Materials(Styles):
    """
    class Materials defines all used materials for the loaded stl models or the
    meshed build programmatically inside the simulator
    """

    def __init__(self) -> None:
        super().__init__()
        self.createMetalRoughMaterials()
        self.createDiffuseSpecularMaterials()
        self.createPhongAlphaMaterials()
        self.createPhongMaterials()

    @staticmethod
    def createMetalRough(
        baseColor: QColor, metalness: float, roughness: float
    ) -> Qt3DExtras.QMetalRoughMaterial:
        material = Qt3DExtras.QMetalRoughMaterial()
        material.setBaseColor(baseColor)
        material.setMetalness(metalness)
        material.setRoughness(roughness)
        return material

    @staticmethod
    def createDiffuseSpecular(
        ambient: RGBA,
        specular: RGBA,
        diffuse: RGBA,
        alphaBlending: bool = False,
        shininess: float | None = None,
    ) -> Qt3DExtras.QDiffuseSpecularMaterial:
        material = Qt3DExtras.QDiffuseSpecularMaterial()
        material.setAmbient(QColor(*ambient))
        material.setSpecular(QColor(*specular))
        material.setDiffuse(QColor(*diffuse))
        material.setAlphaBlendingEnabled(alphaBlending)
        if shininess is not None:
            material.setShininess(shininess)
        return material

    def createPhongAlpha(
        self,
        ambient: list[int],
        diffuse: list[int] | None = None,
        specular: list[int] | None = None,
        alpha: float = 1,
        shininess: float = 64,
    ) -> Qt3DExtras.QPhongAlphaMaterial:
        """diffuse and specular default to the ambient color."""
        material = Qt3DExtras.QPhongAlphaMaterial()
        material.setAmbient(self.rgb2hex(ambient))
        material.setDiffuse(self.rgb2hex(diffuse or ambient))
        material.setSpecular(self.rgb2hex(specular or ambient))
        material.setAlpha(alpha)
        material.setShininess(shininess)
        return material

    def createPhong(
        self, color: list[int], shininess: float | None = None
    ) -> Qt3DExtras.QPhongMaterial:
        material = Qt3DExtras.QPhongMaterial()
        material.setAmbient(self.rgb2hex(color))
        material.setDiffuse(self.rgb2hex(color))
        material.setSpecular(self.rgb2hex(color))
        if shininess is not None:
            material.setShininess(shininess)
        return material

    def createMetalRoughMaterials(self) -> None:
        self.mountBlack = self.createMetalRough(QColor(127, 127, 127), 0.8, 0.5)
        self.aluminiumGrey = self.createMetalRough(QColor(164, 164, 192), 0.3, 0.5)
        self.environ = self.createMetalRough(QColor(*self.M_PRIM2), 0.5, 0.5)
        self.stainless = self.createMetalRough(QColor(255, 255, 255), 0.9, 0.8)
        self.domeColumn = self.createMetalRough(QColor(150, 90, 50), 0, 1)

    def createDiffuseSpecularMaterials(self) -> None:
        self.aluCCD = self.createDiffuseSpecular((32, 32, 92), (64, 64, 255), (32, 32, 92, 255))
        self.aluRed = self.createDiffuseSpecular(
            (128, 32, 32), (255, 255, 255), (128, 32, 32, 255), shininess=200
        )
        self.aluKnobs = self.createDiffuseSpecular(
            (128, 128, 128), (255, 255, 255), (64, 64, 64, 255), shininess=64
        )
        self.white = self.createDiffuseSpecular(
            (224, 224, 224), (224, 224, 224), (224, 224, 224, 255), shininess=128
        )
        self.glass = self.createDiffuseSpecular(
            (0, 0, 112), (0, 0, 112), (128, 128, 192, 64), alphaBlending=True, shininess=128
        )

    def createPhongAlphaMaterials(self) -> None:
        self.domeSphere = self.createPhongAlpha(self.M_PRIM2)
        self.domeSlit = self.createPhongAlpha(self.M_PRIM3)
        self.domeDoor = self.createPhongAlpha(self.M_PRIM3)
        self.walls = self.createPhongAlpha(self.M_SEC1)
        self.horizon = self.createPhongAlpha(self.M_PRIM4, self.M_YELLOW, self.M_YELLOW, alpha=0.35)

    def createPhongMaterials(self) -> None:
        self.pointsRed = self.createPhong(self.M_RED, 64)
        self.pointsGreen = self.createPhong(self.M_GREEN, 64)
        self.points = self.createPhong(self.M_TER)
        self.points.setSpecular(128)
        self.lines = self.createPhong(self.M_GRAY, 0)
        self.pointer = self.createPhong(self.M_PINK1, 255)
        self.laser = self.createPhong(self.M_YELLOW, 255)
