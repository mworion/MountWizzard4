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
import platform
from importlib.resources import as_file, files
from mw4.gui.styles.colors import colors
from mw4.gui.styles.forms import forms
from mw4.gui.styles.images import images
from mw4.gui.styles.styleSheets import BASIC_STYLE, MAC_STYLE, NON_MAC_STYLE
from PySide6.QtGui import QIcon


class Styles:
    colorSet = 0
    cachedStyle = None
    cachedColorSet = None
    if platform.system() == "Darwin":
        STYLE = MAC_STYLE + BASIC_STYLE
    else:
        STYLE = NON_MAC_STYLE + BASIC_STYLE

    @property
    def M_TRANS(self) -> str:
        return colors["M_TRANS"][self.colorSet]

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
        if self.cachedStyle is None or self.cachedColorSet != self.colorSet:
            self.cachedStyle = self.renderStyle(self.STYLE)
            self.cachedColorSet = self.colorSet
        return self.cachedStyle

    def __init__(self):
        super().__init__()
        with as_file(files("mw4").joinpath("assets/icon/mw4.ico")) as icon:
            self.mwIcon = QIcon(str(icon))

    @staticmethod
    def hex2rgb(val: str) -> list[int]:
        val = val.lstrip("#")
        r = int(val[0:2], 16)
        g = int(val[2:4], 16)
        b = int(val[4:6], 16)
        return [r, g, b]

    def calcHexColor(self, val: list[int], f: float) -> str:
        rgb = self.hex2rgb(val)
        rgb = [int(x * f) for x in rgb]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    @staticmethod
    def findKeysInLine(line: str, keyChar: chr) -> list:
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
            line = line.replace(f"${key}$", colors[key][self.colorSet])
        return line

    def replaceForm(self, line: str) -> str:
        for key in self.findKeysInLine(line, "%"):
            if key not in forms:
                continue
            line = line.replace(f"%{key}%", forms[key][self.colorSet])
        return line

    def renderStyle(self, styleRaw: str) -> str:
        lines = []
        for lineItem in styleRaw.split("\n"):
            line = self.replaceForm(lineItem)
            line = self.replaceImage(line)
            line = self.replaceColor(line)
            lines.append(line)
        return "\n".join(lines) + "\n"
