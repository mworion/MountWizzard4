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
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
from collections import namedtuple

Point = namedtuple('Point', 'altitude azimuth')
IParam = namedtuple('IParam', 'expTime binning subFrame fast')
MPoint = namedtuple('MPoint', 'path param point')
