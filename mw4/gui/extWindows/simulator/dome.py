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
from PyQt5.QtGui import QVector3D
from PyQt5.Qt3DCore import QEntity

# local import
from gui.extWindows.simulator.materials import Materials
from gui.extWindows.simulator import tools


class SimulatorDome:

    __all__ = ['SimulatorDome',
               ]

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.model = {}
        self.modelRoot = None

    def create(self, rEntity, show):
        """
        :param rEntity:
        :param show:
        :return:
        """
        if self.model:
            self.modelRoot.setParent(None)

        self.model.clear()
        if not show:
            return False

        self.modelRoot = QEntity(rEntity)
        self.model = {
            'domeFloor': {
                'parent': 'ref',
                'source': 'dome-floor.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumGrey,
            },
            'domeWall': {
                'parent': 'ref',
                'source': 'dome-wall.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome3,
            },
            'domeSphere': {
                'parent': 'ref',
                'source': 'dome-sphere.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome1,
            },
            'domeSlit1': {
                'parent': 'domeSphere',
                'source': 'dome-slit1.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome2,
            },
            'domeSlit2': {
                'parent': 'domeSphere',
                'source': 'dome-slit2.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome2,
            },
            'domeDoor1': {
                'parent': 'domeSphere',
                'source': 'dome-door1.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome2,
            },
            'domeDoor2': {
                'parent': 'domeSphere',
                'source': 'dome-door2.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome2,
            },
        }
        for name in self.model:
            tools.linkModel(self.model, name, self.modelRoot)
        self.updatePositions()
        return True

    def setTransparency(self, transparent):
        """
        :return: True for test purpose
        """
        if not self.model:
            return False

        entities = {
            'domeWall': {
                'trans': Materials().dome3t,
                'solid': Materials().dome3
            },
            'domeSphere': {
                'trans': Materials().dome1t,
                'solid': Materials().dome1
            },
            'domeSlit1': {
                'trans': Materials().dome2t,
                'solid': Materials().dome2
            },
            'domeSlit2': {
                'trans': Materials().dome2t,
                'solid': Materials().dome2
            },
            'domeDoor1': {
                'trans': Materials().dome2t,
                'solid': Materials().dome2
            },
            'domeDoor2': {
                'trans': Materials().dome2t,
                'solid': Materials().dome2
            },
        }
        for entity in entities:
            if transparent:
                self.model[entity]['e'].addComponent(entities[entity]['trans'])

            else:
                self.model[entity]['e'].addComponent(entities[entity]['solid'])
        return True

    def updateSettings(self):
        """
        updateSettings resize parts depending on the setting made in the dome tab. likewise
        some transformations have to be reverted as they are propagated through entity linking.

        :return:
        """
        if not self.model:
            return False

        radius = self.app.mount.geometry.domeRadius * 1000
        scale = 1 + (radius - 1250) / 1250
        corrZ = - (scale - 1) * 800
        self.model['domeFloor']['t'].setScale3D(QVector3D(scale, scale, 1))
        self.model['domeWall']['t'].setScale3D(QVector3D(scale, scale, 1))
        self.model['domeSphere']['t'].setScale3D(QVector3D(scale, scale, scale))
        self.model['domeSphere']['t'].setTranslation(QVector3D(0, 0, corrZ))
        return True

    def updatePositions(self):
        """
        updateDome moves dome components
        you normally have to revert your transformation in linked entities if
        they have fixed sizes because they propagate transformations.
        for the shutter i would like to keep the width setting unscaled with
        increasing dome radius

        :return: success
        """
        if not self.model:
            return False

        if 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION' in self.app.dome.data:
            az = self.app.dome.data['ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION']
            self.model['domeSphere']['t'].setRotationZ(-az)

        if 'DOME_SHUTTER.SHUTTER_OPEN' in self.app.dome.data:
            isOpen = self.app.dome.data['DOME_SHUTTER.SHUTTER_OPEN']
            radius = self.app.mount.geometry.domeRadius * 1000
            scale = 1 + (radius - 1250) / 1250
            width = self.app.dome.clearOpening * 1000
            scaleSlit = (1 + (width - 600) / 600 / 2) * 0.9
            shiftShutter = width / 2 / scale

            self.model['domeSlit1']['t'].setScale3D(QVector3D(1, scaleSlit, 1))
            self.model['domeSlit2']['t'].setScale3D(QVector3D(1, scaleSlit, 1))

            if isOpen:
                self.model['domeDoor1']['t'].setTranslation(QVector3D(0,
                                                                      shiftShutter,
                                                                      0))
                self.model['domeDoor2']['t'].setTranslation(QVector3D(0,
                                                                      -shiftShutter,
                                                                      0))
            else:
                self.model['domeDoor1']['t'].setTranslation(QVector3D(0, 0, 0))
                self.model['domeDoor2']['t'].setTranslation(QVector3D(0, 0, 0))

        return True
