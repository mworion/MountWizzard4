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

# local imports

gradients = {
    "GRAD_1": [
        "",
        "qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:0.15, stop:0 $M_TER$, stop:0.25 $M_TER2$, stop:1 #)",
        "",
        "",
    ],
    "GRAD_2": [
        "",
        "qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:0.0075, stop:0 $M_TER$, stop:0.2 $M_TER2$, stop:1 #)",
        "",
        "",
    ],
}
