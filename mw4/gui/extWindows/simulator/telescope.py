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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PySide6.QtGui import QVector3D

# local import
from gui.extWindows.simulator.tools import linkModel
from gui.extWindows.simulator.materials import Materials


class SimulatorTelescope:
    """ """

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.app.updateDomeSettings.connect(self.updatePositions)

    def updatePositions(self):
        """
        updateSettings resize parts depending on the setting made in the dome
        tab. likewise some transformations have to be reverted as they are
        propagated through entity linking.

        :return:
        """
        if not self.app.deviceStat["mount"]:
            return

        north = self.app.mount.geometry.offNorth * 1000
        east = self.app.mount.geometry.offEast * 1000
        vertical = self.app.mount.geometry.offVert * 1000

        node = self.parent.entityModel.get("mountBase")
        if node:
            node["trans"].setTranslation(QVector3D(north, -east, 1000 + vertical))

        latitude = self.app.mount.obsSite.location.latitude.degrees
        node = self.parent.entityModel.get("lat")
        if node:
            node["trans"].setRotationY(-abs(latitude))

        offPlateOTA = self.app.mount.geometry.offPlateOTA * 1000
        lat = -self.app.mainW.ui.offLAT.value() * 1000

        node = self.parent.entityModel.get("gem")
        if node:
            node["mesh"].setYExtent(abs(lat) + 80)

        node = self.parent.entityModel.get("gem")
        if node:
            node["trans"].setTranslation(QVector3D(159.0, lat / 2, 338.5))

        node = self.parent.entityModel.get("gemCorr")
        if node:
            node["trans"].setTranslation(QVector3D(0.0, lat / 2, 0.0))

        scaleRad = (offPlateOTA - 25) / 55
        scaleRad = max(scaleRad, 1)

        node = self.parent.entityModel.get("otaRing")
        if node:
            node["trans"].setScale3D(QVector3D(1.0, scaleRad, scaleRad))
            node["trans"].setTranslation(QVector3D(0.0, 0.0, -10 * scaleRad + 10))

        node = self.parent.entityModel.get("otaTube")
        if node:
            node["trans"].setScale3D(QVector3D(1.0, scaleRad, scaleRad))
            node["trans"].setTranslation(QVector3D(0.0, 0.0, -10 * scaleRad + 10))

        node = self.parent.entityModel.get("otaImagetrain")
        if node:
            node["trans"].setTranslation(QVector3D(0, 0, 65 * (scaleRad - 1)))

    def updateRotation(self):
        """
        updateMount moves ra and dec axis according to the values in the mount.

        :return:
        """
        angRA = self.app.mount.obsSite.angularPosRA
        angDEC = self.app.mount.obsSite.angularPosDEC
        if not (angRA and angDEC):
            return

        node = self.parent.entityModel.get("ra")
        if node:
            node["trans"].setRotationX(-angRA.degrees + 90)

        node = self.parent.entityModel.get("dec")
        if node:
            node["trans"].setRotationZ(-angDEC.degrees)

    def create(self):
        """ """
        lat = self.app.mount.obsSite.location.latitude.degrees
        model = {
            "mountRoot": {
                "parent": "ref_fusion_m",
            },
            "mountBase": {
                "parent": "mountRoot",
                "source": "mount-base.stl",
                "trans": [0, 0, 1000],
                "mat": Materials().mountBlack,
            },
            "mountKnobs": {
                "parent": "mountBase",
                "source": "mount-base-knobs.stl",
                "mat": Materials().aluKnobs,
            },
            "lat": {
                "parent": "mountBase",
                "trans": [0, 0, 70],
                "rot": [0, -90 + 48, 0],
            },
            "mountRa": {
                "parent": "lat",
                "source": "mount-ra.stl",
                "trans": [0, 0, -70],
                "mat": Materials().mountBlack,
            },
            "ra": {
                "parent": "mountRa",
                "trans": [0, 0, 190],
            },
            "mountDec": {
                "parent": "ra",
                "source": "mount-dec.stl",
                "trans": [0, 0, -190],
                "mat": Materials().mountBlack,
            },
            "mountDecKnobs": {
                "parent": "ra",
                "source": "mount-dec-knobs.stl",
                "trans": [0, 0, -190],
                "mat": Materials().aluKnobs,
            },
            "mountDecWeights": {
                "parent": "ra",
                "source": "mount-dec-weights.stl",
                "trans": [0, 0, -190],
                "mat": Materials().stainless,
            },
            "dec": {
                "parent": "mountDec",
                "trans": [159, 0, 190],
            },
            "mountHead": {
                "parent": "dec",
                "source": "mount-head.stl",
                "trans": [-159, 0, -190],
                "mat": Materials().mountBlack,
            },
            "mountHeadKnobs": {
                "parent": "dec",
                "source": "mount-head-knobs.stl",
                "trans": [-159, 0, -190],
                "mat": Materials().aluKnobs,
            },
            "gem": {
                "parent": "mountHead",
                "source": ["cuboid", 100, 60, 10],
                "trans": [159, 0, 338.5],
                "mat": Materials().aluCCD,
            },
            "gemCorr": {
                "parent": "gem",
                "scale": [1, 1, 1],
            },
            "otaPlate": {
                "parent": "gemCorr",
                "source": "ota-plate.stl",
                "mat": Materials().mountBlack,
            },
            "otaRing": {
                "parent": "otaPlate",
                "source": "ota-ring-s.stl",
                "scale": [1, 1, 1],
                "mat": Materials().mountBlack,
            },
            "otaTube": {
                "parent": "otaPlate",
                "source": "ota-tube-s.stl",
                "scale": [1, 1, 1],
                "mat": Materials().white,
            },
            "otaImagetrain": {
                "parent": "gemCorr",
                "source": "ota-imagetrain.stl",
                "scale": [1, 1, 1],
                "mat": Materials().mountBlack,
            },
            "otaCCD": {
                "parent": "otaImagetrain",
                "source": "ota-ccd.stl",
                "mat": Materials().aluCCD,
            },
            "otaFocus": {
                "parent": "otaImagetrain",
                "source": "ota-focus.stl",
                "mat": Materials().aluRed,
            },
            "otaFocusTop": {
                "parent": "otaImagetrain",
                "source": "ota-focus-top.stl",
                "mat": Materials().white,
            },
        }
        if lat < 0:
            model["mountBase"]["rot"] = [0, 0, 180]

        linkModel(model, self.parent.entityModel)
        self.updateRotation()
        self.updatePositions()
        return True
