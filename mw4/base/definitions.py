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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from collections import namedtuple

# we are adding named tuples for the readability of the code
# fist package is related to modeling procedure and defines the model points
# and the necessary structures for storing the data, which is generated during
# the model run

# the model point itself
Point = namedtuple('Point', 'altitude azimuth')
