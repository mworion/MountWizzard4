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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from logic.databaseProcessing.sourceURL import cometSourceURLs
from logic.databaseProcessing.sourceURL import satSourceURLs
from logic.databaseProcessing.sourceURL import asteroidSourceURLs


a = cometSourceURLs
b = satSourceURLs
c = asteroidSourceURLs
assert isinstance(a, dict)
assert isinstance(b, dict)
assert isinstance(c, dict)

