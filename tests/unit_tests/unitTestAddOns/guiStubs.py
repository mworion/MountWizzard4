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
# License APL2.0
#
###########################################################
from PySide6.QtCore import QObject


class CheckBox:
    checked = False

    def isChecked(self):
        return self.checked

    def setChecked(self, value):
        self.checked = value


class LineEdit:
    valueFloat = 0

    def value(self):
        return self.valueFloat

    def setValue(self, value):
        self.valueFloat = value


class UIStub(QObject):
    def __init__(self):
        from tests.unit_tests.unitTestAddOns.guiStubs import LineEdit
        self.offLAT = LineEdit()


class MainW:
    def __init__(self):
        self.ui = UIStub()
        self.gameControllerRunning = False
