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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
import PyQt5
from indibase import indiBase
# local imports


class Environ(PyQt5.QtWidgets.QWidget):
    """
    the class Environ inherits all information and handling of environment devices

        >>> fw = Environ(
        >>>              )
    """

    __all__ = ['Environ',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 ):
        super().__init__()
