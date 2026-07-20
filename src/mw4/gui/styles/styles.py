############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import numpy as np
import platform
import pyqtgraph as pg
from importlib.resources import as_file, files
from mw4.gui.styles.colors import colors
from mw4.gui.styles.images import images
from mw4.gui.styles.styleSheets import BASIC_STYLE, MAC_STYLE, NON_MAC_STYLE
from PySide6.QtGui import QIcon
from typing import Any


class Styles:
    COLOR_MAPS_STRINGS = ["CET-L2", "plasma", "cividis", "magma", "CET-D1A"]
    STYLE = (
        MAC_STYLE + BASIC_STYLE
        if platform.system() == "Darwin"
        else NON_MAC_STYLE + BASIC_STYLE
    )

    colorSet: int = 0
    cachedColorSet: int = 0
    transparency: float = 1.0
    cachedTransparency: float = 1
    cachedStyle: str = ""

    def __getattr__(self, name: str) -> list:
        if not name.startswith("M_"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )
        if name.endswith("a"):
            val = colors[name[:-1]][self.colorSet].copy()
            val[3] = int(val[3] * self.transparency)
            return val
        else:
            val = colors[name][self.colorSet][0:3]
            return val

    @property
    def mw4Style(self) -> str:
        if (
            not self.cachedStyle
            or self.cachedColorSet != self.colorSet
            or self.cachedTransparency != self.transparency
        ):
            self.cachedStyle = self.renderStyle(self.STYLE)
            self.cachedColorSet = self.colorSet
            self.cachedTransparency = self.transparency
        return self.cachedStyle

    @property
    def colorMapStyle(self) -> list[Any]:
        return self.generateCMaps()

    def __init__(self):
        with as_file(files("mw4").joinpath("assets/icon/mw4.ico")) as icon:
            self.mwIcon = QIcon(str(icon))

    @staticmethod
    def hex2rgb(val: str) -> list[int]:
        val = val.lstrip("#")
        r = int(val[0:2], 16)
        g = int(val[2:4], 16)
        b = int(val[4:6], 16)
        if len(val) > 6:
            return [r, g, b, int(val[6:8], 16)]
        else:
            return [r, g, b]

    @staticmethod
    def rgb2hex(val: list[int]) -> str:
        colHex = f"#{val[0]:02x}{val[1]:02x}{val[2]:02x}"
        if len(val) == 4:
            colHex = f"{colHex}{val[3]:02x}"
        return colHex

    @staticmethod
    def findKeysInLine(line: str, keyChar: str) -> list:
        keys = []
        start = 0
        end = 0
        while start < len(line):
            start = line.find(keyChar, end)
            if start == -1:
                break
            end = line.find(keyChar, start + 1)
            keys.append(line[start + 1 : end])
        return keys

    def replaceImage(self, line: str) -> str:
        for key in self.findKeysInLine(line, "$"):
            if key not in images:
                continue
            keyExt = images[key][self.colorSet]
            with as_file(files("mw4").joinpath(f"assets/icon/{keyExt}.svg")) as imageFile:
                temp = (
                    str(imageFile).replace("\\", "/")
                    if platform.system() == "Windows"
                    else str(imageFile)
                )
                line = line.replace(f"${key}$", temp)
        return line

    def replaceColor(self, line: str) -> str:
        for key in self.findKeysInLine(line, "$"):
            if key not in colors:
                continue
            rgba = colors[key][self.colorSet].copy()
            if key in ["M_BACK", "M_BACK1"]:
                rgba[3] = int(self.transparency * 255)
            color = f"rgba{tuple(rgba)}"
            line = line.replace(f"${key}$", color)
        return line

    def renderStyle(self, styleRaw: str) -> str:
        lines = []
        for lineItem in styleRaw.split("\n"):
            line = self.replaceImage(lineItem)
            line = self.replaceColor(line)
            lines.append(line)
        return "\n".join(lines) + "\n"

    def generateCmapGYR(self) -> pg.ColorMap:
        col = np.array(
            [self.M_GREENa, self.M_YELLOWa, self.M_REDa],
            dtype=np.uint8,
        )
        positions = [0, 0.6, 1.0]
        return pg.ColorMap(positions, col)

    def convertColorMap2Alpha(self, colorMap: str) -> pg.ColorMap:
        cmap = pg.colormap.get(colorMap)
        col = cmap.color
        pos = cmap.pos
        rgba_colors = col.copy()
        rgba_colors[:, 3] = self.transparency
        rgba_colors = rgba_colors * 255
        return pg.ColorMap(pos, rgba_colors.astype(np.uint8))

    def generateCMaps(self):
        colorMaps = [self.generateCmapGYR()]
        for cMapString in self.COLOR_MAPS_STRINGS:
            colorMaps.append(self.convertColorMap2Alpha(cMapString))
        return colorMaps
