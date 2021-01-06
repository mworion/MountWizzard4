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
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtGui import QVector3D
from PyQt5.Qt3DCore import QEntity
from PyQt5.Qt3DExtras import QCuboidMesh

# local import
from gui.extWindows.simulator.materials import Materials
from gui.extWindows.simulator import tools


class SimulatorTelescope:

    __all__ = ['SimulatorTelescope',
               ]

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.model = {}
        self.modelRoot = None

    def create(self, rEntity, show):
        """

        dict {'name of model': {'parent': }}

        :param rEntity: root of the 3D models
        :param show: root of the 3D models
        :return:
        """

        if self.model:
            self.modelRoot.setParent(None)

        self.model.clear()

        if not show:
            return False

        self.modelRoot = QEntity(rEntity)

        self.model = {
            'mountBase': {
                'parent': None,
                'source': 'mount-base.stl',
                'trans': [0, 0, 1000],
                'mat': Materials().aluminiumS,
            },
            'mountKnobs': {
                'parent': 'mountBase',
                'source': 'mount-base-knobs.stl',
                'mat': Materials().aluminium,
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
                'mat': Materials().aluminiumS,
            },
            'ra': {
                'parent': 'mountRa',
                'trans': [0, 0, 190],
            },
            'mountDec': {
                'parent': 'ra',
                'source': 'mount-dec.stl',
                'trans': [0, 0, -190],
                'mat': Materials().aluminiumS,
            },
            'mountDecKnobs': {
                'parent': 'ra',
                'source': 'mount-dec-knobs.stl',
                'trans': [0, 0, -190],
                'mat': Materials().aluminium,
            },
            'mountDecWeights': {
                'parent': 'ra',
                'source': 'mount-dec-weights.stl',
                'trans': [0, 0, -190],
                'mat': Materials().stainless,
            },
            'dec': {
                'parent': 'mountDec',
                'trans': [159, 0, 190],
            },
            'mountHead': {
                'parent': 'dec',
                'source': 'mount-head.stl',
                'trans': [-159, 0, -190],
                'mat': Materials().aluminiumS,
            },
            'mountHeadKnobs': {
                'parent': 'dec',
                'source': 'mount-head-knobs.stl',
                'trans': [-159, 0, -190],
                'mat': Materials().aluminium,
            },
            'gem': {
                'parent': 'mountHead',
                'source': [QCuboidMesh(), 100, 60, 10],
                'trans': [159, 0, 338.5],
                'mat': Materials().aluminiumB,
            },
            'gemCorr': {
                'parent': 'gem',
                'scale': [1, 1, 1],
            },
            'otaPlate': {
                'parent': 'gemCorr',
                'source': 'ota-plate.stl',
                'mat': Materials().aluminiumS,
            },
            'otaRing': {
                'parent': 'otaPlate',
                'source': 'ota-ring-s.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumS,
            },
            'otaTube': {
                'parent': 'otaPlate',
                'source': 'ota-tube-s.stl',
                'scale': [1, 1, 1],
                'mat': Materials().white,
            },
            'otaImagetrain': {
                'parent': 'gemCorr',
                'source': 'ota-imagetrain.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumS,
            },
            'otaCCD': {
                'parent': 'otaImagetrain',
                'source': 'ota-ccd.stl',
                'mat': Materials().aluminiumB,
            },
            'otaFocus': {
                'parent': 'otaImagetrain',
                'source': 'ota-focus.stl',
                'mat': Materials().aluminiumR,
            },
            'otaFocusTop': {
                'parent': 'otaImagetrain',
                'source': 'ota-focus-top.stl',
                'mat': Materials().white,
            },
        }

        for name in self.model:
            tools.linkModel(self.model, name, self.modelRoot)

        return True

    def updateSettings(self):
        """
        updateSettings resize parts depending on the setting made in the dome tab. likewise
        some transformations have to be reverted as they are propagated through entity linking.

        :return:
        """

        if not self.model:
            return False

        north = self.app.mount.geometry.offNorth * 1000
        east = self.app.mount.geometry.offEast * 1000
        vertical = self.app.mount.geometry.offVert * 1000
        self.model['mountBase']['t'].setTranslation(QVector3D(north, -east, 1000 + vertical))

        if self.app.mount.obsSite.location:
            latitude = self.app.mount.obsSite.location.latitude.degrees
            self.model['lat']['t'].setRotationY(- abs(latitude))

        if self.app.mount.geometry.offGemPlate:
            offPlateOTA = self.app.mount.geometry.offPlateOTA * 1000
            lat = - self.app.mainW.ui.offLAT.value() * 1000

            self.model['gem']['m'].setYExtent(abs(lat) + 80)
            self.model['gem']['t'].setTranslation(QVector3D(159.0, lat / 2, 338.5))
            self.model['gemCorr']['t'].setTranslation(QVector3D(0.0, lat / 2, 0.0))

            scaleRad = (offPlateOTA - 25) / 55
            scaleRad = max(scaleRad, 1)

            self.model['otaRing']['t'].setScale3D(QVector3D(1.0, scaleRad, scaleRad))
            self.model['otaRing']['t'].setTranslation(QVector3D(0.0, 0.0, - 10 * scaleRad + 10))
            self.model['otaTube']['t'].setScale3D(QVector3D(1.0, scaleRad, scaleRad))
            self.model['otaTube']['t'].setTranslation(QVector3D(0.0, 0.0, - 10 * scaleRad + 10))
            self.model['otaImagetrain']['t'].setTranslation(QVector3D(0, 0, 65 * (scaleRad - 1)))

        return True

    def updatePositions(self):
        """
        updateMount moves ra and dec axis according to the values in the mount.

        :return:
        """

        if not self.model:
            return False

        angRA = self.app.mount.obsSite.angularPosRA
        angDEC = self.app.mount.obsSite.angularPosDEC

        if not (angRA and angDEC):
            return False

        self.model['ra']['t'].setRotationX(- angRA.degrees + 90)
        self.model['dec']['t'].setRotationZ(- angDEC.degrees)

        return True
