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
# (c) 2019
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

# imaging parameters
IParam = namedtuple('IParam', 'expTime binning subFrame fastReadout')

# modeling parameters
MParam = namedtuple('MParam', 'number count path name astrometry timeout radius')

# modeling generated data for programming the model
MData = namedtuple('MData', 'raMJNow decMJNow raSJNow decSJNow sidereal julian pierside')

# mount retrofit data
RData = namedtuple('RData', 'errorRMS errorRA errorDEC')

# overall structure containing all of the above
MPoint = namedtuple('MPoint', 'mParam iParam point mData rData')


# second cluster is for the astrometry stuff and solving data
# during solving we extract some data from headers and store them

# solving values
Solve = namedtuple('Solve', 'raJ2000 decJ2000 angle scale error flipped')

# overall structure which as well add the solve success part
Solution = namedtuple('Solution', 'success solve')
