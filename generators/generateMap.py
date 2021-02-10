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
# Python  v3.7.3
#
# Michael Würtenberger
#
# written in python3 , (c) 2019, 2020 by mworion
# Licence APL2.0
#
###########################################################
#
# this file is auto generated for the purpose of getting data prepared
# to show the alignment stars in mountwizzard
#
# standard libraries
import pickle
import numpy as np
# external packages
import shapefile
# local import

shapeFile = 'ne_110m_land.shp'
shape = shapefile.Reader(shapeFile)
worldmap = {}

for index, record in enumerate(shape.shapeRecords()):
    x = [i[0] for i in record.shape.points[:]]
    y = [i[1] for i in record.shape.points[:]]
    worldmap[index] = {}
    worldmap[index]['xDeg'] = x
    worldmap[index]['yDeg'] = y
    worldmap[index]['xRad'] = np.radians(x)
    worldmap[index]['yRad'] = np.radians(y)

with open('worldmap.dat', 'wb') as fd:
    pickle.dump(worldmap, fd)

