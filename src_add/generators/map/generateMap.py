############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
import pickle
import numpy as np
import shapefile


shapeFile = "ne_110m_coastline.shp"
shape = shapefile.Reader(shapeFile)
worldmap = {}

for index, record in enumerate(shape.shapeRecords()):
    x = [i[0] for i in record.shape.points[:]]
    y = [i[1] for i in record.shape.points[:]]
    worldmap[index] = {}
    worldmap[index]["xDeg"] = x
    worldmap[index]["yDeg"] = y

with open("worldmap.dat", "wb") as fd:
    pickle.dump(worldmap, fd)
