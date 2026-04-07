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
from mw4.gui.utilities.generateSprites import makePointer, makeSat
from PySide6.QtGui import QPainterPath


def test_makePointer():
    val = makePointer()
    assert isinstance(val, QPainterPath)


def test_makeSat():
    val = makeSat()
    assert isinstance(val, QPainterPath)
