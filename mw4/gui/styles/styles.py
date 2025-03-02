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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import platform

# external packages

# local imports
from mw4.gui.styles.colors import colors
from mw4.gui.styles.gradients import gradients
from mw4.gui.styles.forms import forms
from mw4.gui.styles.styleSheets import NON_MAC_STYLE, MAC_STYLE, BASIC_STYLE


class Styles:
    colorSet = 0

    @property
    def M_TRANS(self):
        return colors["M_TRANS"][self.colorSet]

    @property
    def M_PRIM(self):
        return colors["M_PRIM"][self.colorSet]

    @property
    def M_PRIM1(self):
        return colors["M_PRIM1"][self.colorSet]

    @property
    def M_PRIM2(self):
        return colors["M_PRIM2"][self.colorSet]

    @property
    def M_PRIM3(self):
        return colors["M_PRIM3"][self.colorSet]

    @property
    def M_PRIM4(self):
        return colors["M_PRIM4"][self.colorSet]

    @property
    def M_SEC(self):
        return colors["M_SEC"][self.colorSet]

    @property
    def M_SEC1(self):
        return colors["M_SEC1"][self.colorSet]

    @property
    def M_TER(self):
        return colors["M_TER"][self.colorSet]

    @property
    def M_TER1(self):
        return colors["M_TER1"][self.colorSet]

    @property
    def M_TER2(self):
        return colors["M_TER2"][self.colorSet]

    @property
    def M_BACK(self):
        return colors["M_BACK"][self.colorSet]

    @property
    def M_BACK1(self):
        return colors["M_BACK1"][self.colorSet]

    @property
    def M_GRAY(self):
        return colors["M_GRAY"][self.colorSet]

    @property
    def M_RED(self):
        return colors["M_RED"][self.colorSet]

    @property
    def M_RED1(self):
        return colors["M_RED1"][self.colorSet]

    @property
    def M_RED2(self):
        return colors["M_RED2"][self.colorSet]

    @property
    def M_YELLOW(self):
        return colors["M_YELLOW"][self.colorSet]

    @property
    def M_YELLOW1(self):
        return colors["M_YELLOW1"][self.colorSet]

    @property
    def M_YELLOW2(self):
        return colors["M_YELLOW2"][self.colorSet]

    @property
    def M_GREEN(self):
        return colors["M_GREEN"][self.colorSet]

    @property
    def M_GREEN1(self):
        return colors["M_GREEN1"][self.colorSet]

    @property
    def M_GREEN2(self):
        return colors["M_GREEN2"][self.colorSet]

    @property
    def M_PINK(self):
        return colors["M_PINK"][self.colorSet]

    @property
    def M_PINK1(self):
        return colors["M_PINK1"][self.colorSet]

    @property
    def M_CYAN(self):
        return colors["M_CYAN"][self.colorSet]

    @property
    def M_CYAN1(self):
        return colors["M_CYAN1"][self.colorSet]

    @property
    def M_TAB(self):
        return colors["M_TAB"][self.colorSet]

    @property
    def M_TAB1(self):
        return colors["M_TAB1"][self.colorSet]

    @property
    def M_TAB2(self):
        return colors["M_TAB2"][self.colorSet]

    @property
    def mw4Style(self) -> str:
        if platform.system() == "Darwin":
            styleRaw = MAC_STYLE + BASIC_STYLE
        else:
            styleRaw = NON_MAC_STYLE + BASIC_STYLE
        return self.renderStyle(styleRaw)

    @staticmethod
    def hex2rgb(val: str) -> list[int]:
        """ """
        val = val.lstrip("#")
        r = int(val[0:2], 16)
        g = int(val[2:4], 16)
        b = int(val[4:6], 16)
        return [r, g, b]

    def calcHexColor(self, val: list[int], f: float) -> str:
        """ """
        rgb = self.hex2rgb(val)
        rgb = [int(x * f) for x in rgb]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    @staticmethod
    def findKeysInLine(line: str, keyChar: chr) -> list:
        """ """
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

    def replaceColor(self, line: str) -> str:
        """ """
        for key in self.findKeysInLine(line, "$"):
            if key not in colors:
                continue
            line = line.replace(f"${key}$", colors[key][self.colorSet])
        return line

    def replaceForm(self, line: str) -> str:
        """ """
        for key in self.findKeysInLine(line, "%"):
            if key not in forms:
                continue
            line = line.replace(f"%{key}%", forms[key][self.colorSet])
        return line

    def insertGradient(self, line: str) -> str:
        """ """
        for key in self.findKeysInLine(line, "#"):
            keyPair = key.split(",")
            if len(keyPair) != 2 or keyPair[0] not in gradients:
                continue
            insertItem = gradients[keyPair[0]][self.colorSet]
            if insertItem:
                insertItem = insertItem.replace("#", keyPair[1])
            else:
                insertItem = keyPair[1]
            line = line.replace(f"#{key}#", insertItem)
        return line

    def renderStyle(self, styleRaw: str) -> str:
        """ """
        style = ""
        for line in styleRaw.split("\n"):
            line = self.insertGradient(line)
            line = self.replaceForm(line)
            line = self.replaceColor(line)
            style += line + "\n"
        return style
