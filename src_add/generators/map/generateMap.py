############################################################
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
# License APL2.0
#
###########################################################
import numpy as np
import shapefile

# ---------------------------------------------------------------------------
# Output format: worldmap.npz  (numpy compressed)
#
#   x        float64[N]  – all shoreline x-coordinates (longitude), concatenated
#   y        float64[N]  – all shoreline y-coordinates (latitude),  concatenated
#   lengths  int32[S]    – number of points in each of the S segments
#
# To reconstruct the original segment dict at load time:
#   offset = 0
#   for i, length in enumerate(lengths):
#       x_seg = x[offset:offset + length]
#       y_seg = y[offset:offset + length]
#       offset += length
# ---------------------------------------------------------------------------

shapeFile = "ne_50m_land.shp"
shape = shapefile.Reader(shapeFile)

all_x: list[np.ndarray] = []
all_y: list[np.ndarray] = []
lengths: list[int] = []

for record in shape.shapeRecords():
    points = record.shape.points[:]
    seg_x = np.array([p[0] for p in points], dtype=np.float64)
    seg_y = np.array([p[1] for p in points], dtype=np.float64)
    all_x.append(seg_x)
    all_y.append(seg_y)
    lengths.append(len(points))

np.savez_compressed(
    "worldmap.npz",
    x=np.concatenate(all_x),
    y=np.concatenate(all_y),
    lengths=np.array(lengths, dtype=np.int32),
)
