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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from gui.utilities.toolsQtWidget import MWidget


class ModelStatus(MWidget):
    """
    """
    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        ms = self.app.mount.signals
        ms.alignDone.connect(self.updateAlignGUI)
        ms.alignDone.connect(self.updateTurnKnobsGUI)

    def setupIcons(self) -> None:
        """
        """
        pixmap = self.img2pixmap(':/pics/azimuth.png').scaled(140, 140)
        self.ui.picAZ.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/pics/altitude.png').scaled(140, 140)
        self.ui.picALT.setPixmap(pixmap)

    def updateAlignGUI(self, model):
        """
        """
        self.guiSetText(self.ui.numberStars, '2.0f', model.numberStars)
        self.guiSetText(self.ui.numberStars1, '2.0f', model.numberStars)
        self.guiSetText(self.ui.errorRMS, '5.1f', model.errorRMS)
        self.guiSetText(self.ui.errorRMS1, '5.1f', model.errorRMS)
        self.guiSetText(self.ui.terms, '2.0f', model.terms)
        val = None if model.positionAngle is None else model.positionAngle.degrees
        self.guiSetText(self.ui.positionAngle, '5.1f', val)
        val = None if model.polarError is None else model.polarError.degrees * 3600
        self.guiSetText(self.ui.polarError, '5.0f', val)
        val = None if model.orthoError is None else model.orthoError.degrees * 3600
        self.guiSetText(self.ui.orthoError, '5.0f', val)
        val = None if model.azimuthError is None else model.azimuthError.degrees
        self.guiSetText(self.ui.azimuthError, '5.1f', val)
        val = None if model.altitudeError is None else model.altitudeError.degrees
        self.guiSetText(self.ui.altitudeError, '5.1f', val)

    def updateTurnKnobsGUI(self, model):
        """
        """
        if model.azimuthTurns is not None:
            if model.azimuthTurns > 0:
                text = '{0:3.1f} revs left'.format(abs(model.azimuthTurns))
            else:
                text = '{0:3.1f} revs right'.format(abs(model.azimuthTurns))
        else:
            text = '-'

        self.ui.azimuthTurns.setText(text)
        if model.altitudeTurns is not None:
            if model.altitudeTurns > 0:
                text = '{0:3.1f} revs down'.format(abs(model.altitudeTurns))
            else:
                text = '{0:3.1f} revs up'.format(abs(model.altitudeTurns))
        else:
            text = '-'

        self.ui.altitudeTurns.setText(text)