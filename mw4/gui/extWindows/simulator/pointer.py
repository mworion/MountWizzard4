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
from PyQt5.Qt3DExtras import QSphereMesh

# local import
from gui.extWindows.simulator.materials import Materials
from gui.extWindows.simulator import tools


class SimulatorPointer:

    __all__ = ['SimulatorPointer',
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
        :return: success
        """
        if self.model:
            self.modelRoot.setParent(None)

        self.model.clear()
        if not show:
            return False

        self.modelRoot = QEntity(rEntity)

        self.model = {
            'pointer': {
                'parent': None,
                'source': [QSphereMesh(), 50, 30, 30],
                'scale': [1, 1, 1],
                'mat': Materials().pointer,
            },
        }
        for name in self.model:
            tools.linkModel(self.model, name, self.modelRoot)

        self.updatePositions()
        return True

    def updatePositions(self):
        """
        updatePositions calculates the crossing point of the actual telescope view and the
        dome if present.

        :return:
        """
        if not self.model:
            return False
        if not self.app.mount.obsSite.haJNow:
            return False

        lat = self.app.mount.obsSite.location.latitude
        ha = self.app.mount.obsSite.haJNow
        dec = self.app.mount.obsSite.decJNow
        pierside = self.app.mount.obsSite.pierside

        geometry = self.app.mount.geometry
        _, _, intersect, _, _ = geometry.calcTransformationMatrices(ha=ha,
                                                                    dec=dec,
                                                                    lat=lat,
                                                                    pierside=pierside)
        intersect *= 1000
        intersect[2] += 1000

        self.model['pointer']['t'].setTranslation(
            QVector3D(intersect[0],
                      intersect[1],
                      intersect[2]))
        return True
