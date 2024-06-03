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
from gui.extWindows.simulator.tools import linkModel, getTransformation


class SimulatorPointer:

    __all__ = ['SimulatorPointer']

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.app.mount.signals.pointDone.connect(self.updatePositions)
        self.parent.ui.showPointer.checkStateChanged.connect(self.showEnable)

    def showEnable(self):
        """
        """
        isVisible = self.parent.ui.showPointer.isChecked()
        entity = self.parent.entityModel.get('pointer')
        if entity:
            entity.setEnabled(isVisible)

    def updatePositions(self):
        """
        """
        _, _, intersect, _, _ = self.app.mount.calcTransformationMatricesActual()

        if intersect is None:
            return False

        intersect *= 1000
        intersect[2] += 1000

        nodeT = getTransformation(self.parent.entityModel.get('pointerDot'))
        if nodeT:
            nodeT.setTranslation(QVector3D(intersect[0], intersect[1], intersect[2]))

        return True

    def create(self):
        """
        """
        model = {
            'pointer': {
                'parent': 'ref_fusion_m',
            },
            'pointerDot': {
                'parent': 'pointer',
                'source': [Qt3DExtras.QSphereMesh(), 50, 30, 30],
                'scale': [1, 1, 1],
                'mat': self.parent.materials.pointer,
            },
        }
        linkModel(model, self.parent.entityModel)
        self.updatePositions()
        self.showEnable()
