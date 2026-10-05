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
from enum import IntEnum


class OperationStatus(IntEnum):
    IDLE = 0
    MODEL_BATCH = 1
    MODEL_FILE = 2
    MODEL_SYNC = 3
    MODEL_ITERATIVE = 4
    EXPOSE_1 = 5
    EXPOSE_N = 6
    SOLVE = 7
