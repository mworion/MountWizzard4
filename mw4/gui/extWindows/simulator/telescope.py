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
from PySide6.QtGui import QVector3D
from PySide6.Qt3DExtras import Qt3DExtras

# local import
from gui.extWindows.simulator.tools import linkModel, getTransformation, getMesh


class SimulatorTelescope:

    __all__ = ['SimulatorTelescope']

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.app.updateDomeSettings.connect(self.updatePositions)
        self.app.mount.signals.pointDone.connect(self.updateRotation)

    def updatePositions(self):
        """
        updateSettings resize parts depending on the setting made in the dome
        tab. likewise some transformations have to be reverted as they are
        propagated through entity linking.

        :return:
        """
        north = self.app.mount.geometry.offNorth * 1000
        east = self.app.mount.geometry.offEast * 1000
        vertical = self.app.mount.geometry.offVert * 1000

        nodeT = getTransformation(self.parent.entityModel.get('mountBase'))
        if nodeT:
            nodeT.setTranslation(QVector3D(north, -east, 1000 + vertical))

        latitude = self.app.mount.obsSite.location.latitude.degrees
        nodeT = getTransformation(self.parent.entityModel.get('lat'))
        if nodeT:
            nodeT.setRotationY(- abs(latitude))

        offPlateOTA = self.app.mount.geometry.offPlateOTA * 1000
        lat = - self.app.mainW.ui.offLAT.value() * 1000

        nodeM = getMesh(self.parent.entityModel.get('gem'))
        if nodeM:
            nodeM.setYExtent(abs(lat) + 80)

        nodeT = getTransformation(self.parent.entityModel.get('gem'))
        if nodeT:
            nodeT.setTranslation(QVector3D(159.0, lat / 2, 338.5))

        nodeT = getTransformation(self.parent.entityModel.get('gemCorr'))
        if nodeT:
            nodeT.setTranslation(QVector3D(0.0, lat / 2, 0.0))

        scaleRad = (offPlateOTA - 25) / 55
        scaleRad = max(scaleRad, 1)

        nodeT = getTransformation(self.parent.entityModel.get('otaRing'))
        if nodeT:
            nodeT.setScale3D(QVector3D(1.0, scaleRad, scaleRad))
            nodeT.setTranslation(QVector3D(0.0, 0.0, - 10 * scaleRad + 10))

        nodeT = getTransformation(self.parent.entityModel.get('otaTube'))
        if nodeT:
            nodeT.setScale3D(QVector3D(1.0, scaleRad, scaleRad))
            nodeT.setTranslation(QVector3D(0.0, 0.0, - 10 * scaleRad + 10))

        nodeT = getTransformation(self.parent.entityModel.get('otaImagetrain'))
        if nodeT:
            nodeT.setTranslation(QVector3D(0, 0, 65 * (scaleRad - 1)))

    def updateRotation(self):
        """
        updateMount moves ra and dec axis according to the values in the mount.

        :return:
        """
        angRA = self.app.mount.obsSite.angularPosRA
        angDEC = self.app.mount.obsSite.angularPosDEC
        if not (angRA and angDEC):
            return False

        nodeT = getTransformation(self.parent.entityModel.get('ra'))
        if nodeT:
            nodeT.setRotationX(- angRA.degrees + 90)

        nodeT = getTransformation(self.parent.entityModel.get('dec'))
        if nodeT:
            nodeT.setRotationZ(- angDEC.degrees)
        return True

    def create(self):
        """
        """
        lat = self.app.mount.obsSite.location.latitude.degrees
        model = {
            'mount': {
                'parent': 'ref_fusion_m',
            },
            'mountBase': {
                'parent': 'mount',
                'source': 'mount-base.stl',
                'trans': [0, 0, 1000],
                'mat': self.parent.materials.mountBlack,
            },
            'mountKnobs': {
                'parent': 'mountBase',
                'source': 'mount-base-knobs.stl',
                'mat': self.parent.materials.aluKnobs,
            },
            'lat': {
                'parent': 'mountBase',
                'trans': [0, 0, 70],
                'rot': [0, -90 + 48, 0],
            },
            'mountRa': {
                'parent': 'lat',
                'source': 'mount-ra.stl',
                'trans': [0, 0, -70],
                'mat': self.parent.materials.mountBlack,
            },
            'ra': {
                'parent': 'mountRa',
                'trans': [0, 0, 190],
            },
            'mountDec': {
                'parent': 'ra',
                'source': 'mount-dec.stl',
                'trans': [0, 0, -190],
                'mat': self.parent.materials.mountBlack,
            },
            'mountDecKnobs': {
                'parent': 'ra',
                'source': 'mount-dec-knobs.stl',
                'trans': [0, 0, -190],
                'mat': self.parent.materials.aluKnobs,
            },
            'mountDecWeights': {
                'parent': 'ra',
                'source': 'mount-dec-weights.stl',
                'trans': [0, 0, -190],
                'mat': self.parent.materials.stainless,
            },
            'dec': {
                'parent': 'mountDec',
                'trans': [159, 0, 190],
            },
            'mountHead': {
                'parent': 'dec',
                'source': 'mount-head.stl',
                'trans': [-159, 0, -190],
                'mat': self.parent.materials.mountBlack,
            },
            'mountHeadKnobs': {
                'parent': 'dec',
                'source': 'mount-head-knobs.stl',
                'trans': [-159, 0, -190],
                'mat': self.parent.materials.aluKnobs,
            },
            'gem': {
                'parent': 'mountHead',
                'source': [Qt3DExtras.QCuboidMesh(), 100, 60, 10],
                'trans': [159, 0, 338.5],
                'mat': self.parent.materials.aluCCD,
            },
            'gemCorr': {
                'parent': 'gem',
                'scale': [1, 1, 1],
            },
            'otaPlate': {
                'parent': 'gemCorr',
                'source': 'ota-plate.stl',
                'mat': self.parent.materials.mountBlack,
            },
            'otaRing': {
                'parent': 'otaPlate',
                'source': 'ota-ring-s.stl',
                'scale': [1, 1, 1],
                'mat': self.parent.materials.mountBlack,
            },
            'otaTube': {
                'parent': 'otaPlate',
                'source': 'ota-tube-s.stl',
                'scale': [1, 1, 1],
                'mat': self.parent.materials.white,
            },
            'otaImagetrain': {
                'parent': 'gemCorr',
                'source': 'ota-imagetrain.stl',
                'scale': [1, 1, 1],
                'mat': self.parent.materials.mountBlack,
            },
            'otaCCD': {
                'parent': 'otaImagetrain',
                'source': 'ota-ccd.stl',
                'mat': self.parent.materials.aluCCD,
            },
            'otaFocus': {
                'parent': 'otaImagetrain',
                'source': 'ota-focus.stl',
                'mat': self.parent.materials.aluRed,
            },
            'otaFocusTop': {
                'parent': 'otaImagetrain',
                'source': 'ota-focus-top.stl',
                'mat': self.parent.materials.white,
            },
        }
        if lat < 0:
            model['mountBase']['rot'] = [0, 0, 180]

        linkModel(model, self.parent.entityModel)
        self.updateRotation()
        self.updatePositions()
        return True
