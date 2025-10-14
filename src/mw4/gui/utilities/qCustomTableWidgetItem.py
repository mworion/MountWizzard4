############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
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
        selfDataValue = 99 if selfData == "" else float(selfData)
        otherData = other.data(Qt.ItemDataRole.EditRole)
        otherDataValue = 99 if otherData == "" else float(otherData)
        return selfDataValue < otherDataValue
