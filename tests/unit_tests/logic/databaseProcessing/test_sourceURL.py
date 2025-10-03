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

# local import
from logic.databaseProcessing.sourceURL import (
    asteroidSourceURLs,
    cometSourceURLs,
    satSourceURLs,
)

a = cometSourceURLs
b = satSourceURLs
c = asteroidSourceURLs
assert isinstance(a, dict)
assert isinstance(b, dict)
assert isinstance(c, dict)
