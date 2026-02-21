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
# Licence APL2.0
#
###########################################################
from PySide6.QtGui import QPainterPath, QTransform
from PySide6.QtCore import QPoint


def makePointer() -> QPainterPath:
    """ """
    path = QPainterPath()
    path.moveTo(0, -1)
    path.lineTo(0, 1)
    path.moveTo(-1, 0)
    path.lineTo(1, 0)
    path.addEllipse(-0.1, -0.1, 0.2, 0.2)
    path.addEllipse(-0.3, -0.3, 0.6, 0.6)
    return path


def makeSat() -> QPainterPath:
    """ """
    pathPaddles = QPainterPath()
    tr = QTransform()
    pathPaddles.addRect(-0.4, -0.15, 0.1, 0.3)
    pathPaddles.addRect(-0.25, -0.15, 0.1, 0.3)
    tr.rotate(180)
    pathPaddles.addPath(tr.map(pathPaddles))

    pathBody = QPainterPath()
    pathBody.addRect(-0.1, -0.1, 0.2, 0.2)
    pathBody.addEllipse(-0.08, -0.3, 0.16, 0.16)
    pathBody.addEllipse(-0.05, -0.05, 0.1, 0.1)

    path = QPainterPath()
    path.addPath(pathPaddles)
    path.addPath(pathBody)
    tr.rotate(45)
    path = tr.map(path)
    return path
