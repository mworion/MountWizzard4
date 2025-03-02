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
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class QCustomTableWidgetItem(QTableWidgetItem):
    """
    This class reimplements the comparison for item, which are normally float
    values as the standard sorting in this item only supports strings.
    """

    def __init__(self, value):
        super().__init__(value)

    def __lt__(self, other):
        selfData = self.data(Qt.ItemDataRole.EditRole)
        if selfData == "":
            selfDataValue = 99
        else:
            selfDataValue = float(selfData)
        otherData = other.data(Qt.ItemDataRole.EditRole)
        if otherData == "":
            otherDataValue = 99
        else:
            otherDataValue = float(otherData)
        return selfDataValue < otherDataValue
