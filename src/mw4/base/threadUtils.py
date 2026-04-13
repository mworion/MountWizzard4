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
from PySide6.QtCore import QEventLoop, QTimer


def mainThreadSleep(value: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(value, loop.quit)
    loop.exec()


