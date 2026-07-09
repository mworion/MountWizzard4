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

    # ------------------------------------------------------------------
    # Mapping protocol — keeps ``"x" in dReg`` and ``dReg["x"]`` working
    # ------------------------------------------------------------------
    def __iter__(self) -> Iterator[str]:
        return iter(colors)

    def __getitem__(self, name: str) -> list:
        return colors["M_PRIM"][self.colorSet]

    def __contains__(self, name: object) -> bool:
        return name in colors

    @property
    def M_PRIM(self) -> str:
        return colors["M_PRIM"][self.colorSet]

    @property
    def M_PRIM1(self) -> str:
        return colors["M_PRIM1"][self.colorSet]

    @property
    def M_PRIM2(self) -> str:
        return colors["M_PRIM2"][self.colorSet]

    @property
    def M_PRIM3(self) -> str:
        return colors["M_PRIM3"][self.colorSet]

    @property
    def M_PRIM4(self) -> str:
        return colors["M_PRIM4"][self.colorSet]

    @property
    def M_SEC(self) -> str:
        return colors["M_SEC"][self.colorSet]

    @property
    def M_SEC1(self) -> str:
        return colors["M_SEC1"][self.colorSet]

    @property
    def M_TER(self) -> str:
        return colors["M_TER"][self.colorSet]

    @property
    def M_TER1(self) -> str:
        return colors["M_TER1"][self.colorSet]

    @property
    def M_TER2(self) -> str:
        return colors["M_TER2"][self.colorSet]

    @property
    def M_BACK(self) -> str:
        return colors["M_BACK"][self.colorSet]

    @property
    def M_BACK1(self) -> str:
        return colors["M_BACK1"][self.colorSet]

    @property
    def M_GRAY(self) -> str:
        return colors["M_GRAY"][self.colorSet]

    @property
    def M_RED(self) -> str:
        return colors["M_RED"][self.colorSet]

    @property
    def M_RED1(self) -> str:
        return colors["M_RED1"][self.colorSet]

    @property
    def M_RED2(self) -> str:
        return colors["M_RED2"][self.colorSet]

    @property
    def M_YELLOW(self) -> str:
        return colors["M_YELLOW"][self.colorSet]

    @property
    def M_YELLOW1(self):
        return colors["M_YELLOW1"][self.colorSet]

    @property
    def M_YELLOW2(self) -> str:
        return colors["M_YELLOW2"][self.colorSet]

    @property
    def M_GREEN(self) -> str:
        return colors["M_GREEN"][self.colorSet]

    @property
    def M_GREEN1(self) -> str:
        return colors["M_GREEN1"][self.colorSet]

    @property
    def M_GREEN2(self) -> str:
        return colors["M_GREEN2"][self.colorSet]

    @property
    def M_PINK(self) -> str:
        return colors["M_PINK"][self.colorSet]

    @property
    def M_PINK1(self) -> str:
        return colors["M_PINK1"][self.colorSet]

    @property
    def M_CYAN(self) -> str:
        return colors["M_CYAN"][self.colorSet]

    @property
    def M_CYAN1(self) -> str:
        return colors["M_CYAN1"][self.colorSet]

    @property
    def M_TAB(self) -> str:
        return colors["M_TAB"][self.colorSet]

    @property
    def M_TAB1(self) -> str:
        return colors["M_TAB1"][self.colorSet]

    @property
    def M_TAB2(self) -> str:
        return colors["M_TAB2"][self.colorSet]

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
    def rgb2hex(val: list[float]) -> str:
        colHex = f"#{val[0]:02x}{val[1]:02x}{val[2]:02x}"
        if len(val) == 4:
            colHex = f"{colHex}{val[3]:02x}"
        return colHex

    def calcHexColor(self, val: str, f: float) -> str:
        rgb = self.hex2rgb(val)
        rgb = [int(x * f) for x in rgb]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

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
            color = colors[key][self.colorSet]
            if key in ["M_BACK"]:
                r, g, b = self.hex2rgb(color)
                color = f"rgba({r},{g},{b},{self.transparency})"
            if key in ["M_BACK1"]:
                r, g, b = self.hex2rgb(color)
                color = f"rgba({r},{g},{b},{min(3 * self.transparency, 1)})"
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
            [
                self.hex2rgb(f"{self.M_GREEN}40"),
                self.hex2rgb(f"{self.M_YELLOW}40"),
                self.hex2rgb(f"{self.M_RED}40"),
            ],
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

    def addAlpha2ColorString(self, color: str) -> str:
        val = self.hex2rgb(color)
        val.append(int(self.transparency * 255))
        return self.rgb2hex(val)
