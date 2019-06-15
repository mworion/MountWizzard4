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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
import PyQt5
from skyfield.api import Loader

load = Loader('.',
              expire=False,
              verbose=True,
              )

if __name__ == "__main__":
    stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    satellites = load.tle(stations_url)
    satellite = satellites['ISS (ZARYA)']
    print(satellite)
    stations_url = 'http://www.celestrak.com/NORAD/elements/visual.txt'
    satellites = load.tle(stations_url)
    satellite = satellites['ISS (ZARYA)']
    print(satellite)
