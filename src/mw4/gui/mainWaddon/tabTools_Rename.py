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
from astropy.io import fits
from collections.abc import Callable
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.qtFileDialog import MWFileDialog
from pathlib import Path
from PySide6.QtWidgets import QApplication, QListView
from typing import Any


class Rename(TabAddon):
    HEADER_FORMATTERS: dict[str, Callable[[str | float], str]] = {
        "DATE-OBS": lambda e: str(e).replace(":", "-").replace("T", "_").split(".")[0],
        "XBINNING": lambda e: f"Bin{e:1.0f}",
        "CCD-TEMP": lambda e: f"Temp{e:03.0f}",
        "FRAME": str,
        "IMAGETYP": str,
        "FILTER": str,
        "EXPTIME": lambda e: f"Exp{e:1.0f}s",
    }

    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.renameDir: Path = Path()

        self.selectorsDropDowns = {
            "rename1": self.ui.rename1,
            "rename2": self.ui.rename2,
            "rename3": self.ui.rename3,
            "rename4": self.ui.rename4,
            "rename5": self.ui.rename5,
            "rename6": self.ui.rename6,
        }
        self.fitsHeaderKeywords = {
            "None": [""],
            "Datetime": ["DATE-OBS"],
            "Frame": ["FRAME", "IMAGETYP"],
            "Filter": ["FILTER"],
            "Binning": ["XBINNING"],
            "Exp Time": ["EXPTIME"],
            "CCD Temp": ["CCD-TEMP"],
        }
        self.setupGuiTools()
        self.ui.renameStart.clicked.connect(self.renameRunGUI)
        self.ui.renameInputSelect.clicked.connect(self.chooseDir)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        imageDir = str(self.app.mwGlob["imageDir"])
        renameDir = config.get("renameDir", imageDir)
        self.ui.renameDir.setText(renameDir)
        self.renameDir = Path(renameDir)
        self.ui.newObjectName.setText(config.get("newObjectName", ""))
        self.ui.includeSubdirs.setChecked(config.get("includeSubdirs", False))
        for name, ui in self.selectorsDropDowns.items():
            ui.setCurrentIndex(config.get(name, 0))
        self.ui.renameProgress.setValue(0)

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["renameDir"] = self.ui.renameDir.text()
        config["newObjectName"] = self.ui.newObjectName.text()
        config["includeSubdirs"] = self.ui.includeSubdirs.isChecked()
        for name, ui in self.selectorsDropDowns.items():
            config[name] = ui.currentIndex()

    def setupIcons(self) -> None:
        self.mainW.wIcon(self.ui.renameStart, "start")
        self.mainW.wIcon(self.ui.renameInputSelect, "folder")

    def setupGuiTools(self) -> None:
        for name, selectorUI in self.selectorsDropDowns.items():
            selectorUI.clear()
            selectorUI.setView(QListView())
            for headerEntry in self.fitsHeaderKeywords:
                selectorUI.addItem(headerEntry)

    def getNumberFiles(self, search: str) -> int:
        return sum(1 for _ in self.renameDir.glob(search))

    def convertHeaderEntry(self, entry: str | float, fitsKey: str) -> str:
        formatter = self.HEADER_FORMATTERS.get(fitsKey)
        if formatter is None:
            return ""
        return formatter(entry)

    def processSelectors(self, fitsHeader: dict, selection: str) -> str:
        nameChunk = ""
        fitsKeywords = self.fitsHeaderKeywords[selection]
        for fitsKey in fitsKeywords:
            if fitsKey not in fitsHeader:
                continue
            nameChunk = self.convertHeaderEntry(entry=fitsHeader[fitsKey], fitsKey=fitsKey)
            break
        return nameChunk

    def renameFile(self, fileName: Path) -> None:
        with fits.open(name=fileName) as fd:
            fitsHeader = fd[0].header
            newObjectName = self.ui.newObjectName.text().upper()
            newFileName = newObjectName or fitsHeader.get("OBJECT", "UNKNOWN").upper()

            for _, selector in self.selectorsDropDowns.items():
                selection = selector.currentText()
                chunk = self.processSelectors(fitsHeader, selection)
                if chunk:
                    newFileName += f"_{chunk}"
            newFileName = (self.renameDir / newFileName).with_suffix(".fits")
            fileName.rename(newFileName)

    def renameRunGUI(self) -> None:
        includeSubdirs = self.ui.includeSubdirs.isChecked()
        if not self.renameDir.is_dir():
            self.msg.emit(2, "Tools", "Rename error", "No valid input directory given")
            return

        search = "**/*.fit*" if includeSubdirs else "*.fit*"
        numberFiles = self.getNumberFiles(search=search)
        if not numberFiles:
            self.msg.emit(2, "Tools", "Rename error", "No files to rename")
            return

        for i, fileName in enumerate(self.renameDir.glob(search)):
            self.ui.renameProgress.setValue(int(100 * (i + 1) / numberFiles))
            QApplication.processEvents()
            self.renameFile(fileName)

        self.msg.emit(0, "Tools", "Rename", f"{numberFiles:d} images were renamed")

    def chooseDir(self) -> None:
        folder = self.ui.renameDir.text()
        self.renameDir = MWFileDialog.getExistingDirectory(
            self.mainW, "Choose Input Dir", folder
        )
        self.ui.renameDir.setText(str(self.renameDir))
        self.ui.renameProgress.setValue(0)
