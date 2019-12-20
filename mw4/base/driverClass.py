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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
import PyQt5
# local imports


class DriverClass(PyQt5.QtCore.QObject):
    """
    the class DriverClass inherits all information and handling of indi devices
    this class will be only referenced from other classes and not directly used

        >>> dc = DriverClass()
    """

    __all__ = ['DriverClass']

    logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

        # minimum set for driver package built in
        self.name = 'local'
        self.framework = 'local'
        self.run = {
            'local': self
        }

