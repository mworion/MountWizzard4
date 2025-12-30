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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
import os
from astropy.io import fits
from pathlib import Path
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QListView


class Rename(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
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
            "Exp Time": ["exposureTime"],
            "CCD Temp": ["CCD-TEMP"],
        }
        self.setupGuiTools()
        self.ui.renameStart.clicked.connect(self.renameRunGUI)
        self.ui.renameInputSelect.clicked.connect(self.chooseDir)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
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
        """ """
        config = self.app.config["mainW"]
        config["renameDir"] = self.ui.renameDir.text()
        config["newObjectName"] = self.ui.newObjectName.text()
        config["includeSubdirs"] = self.ui.includeSubdirs.isChecked()
        for name, ui in self.selectorsDropDowns.items():
            config[name] = ui.currentIndex()

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.renameStart, "start")
        self.mainW.wIcon(self.ui.renameInputSelect, "folder")

    def setupGuiTools(self) -> None:
        """ """
        for name, selectorUI in self.selectorsDropDowns.items():
            selectorUI.clear()
            selectorUI.setView(QListView())
            for headerEntry in self.fitsHeaderKeywords:
                selectorUI.addItem(headerEntry)

    def getNumberFiles(self, search: str) -> int:
        """ """
        return sum(1 for _ in self.renameDir.glob(search))

    @staticmethod
    def convertHeaderEntry(entry: str, fitsKey: str) -> str:
        """ """
        if fitsKey == "DATE-OBS":
            chunk = entry.replace(":", "-")
            chunk = chunk.replace("T", "_")
            chunk = chunk.split(".")[0]
        elif fitsKey == "XBINNING":
            chunk = f"Bin{entry:1.0f}"
        elif fitsKey == "CCD-TEMP":
            chunk = f"Temp{entry:03.0f}"
        elif fitsKey == "FRAME" or fitsKey == "FILTER":
            chunk = f"{entry}"
        elif fitsKey == "EXPTIME":
            chunk = f"Exp{entry:1.0f}s"
        else:
            chunk = ""

        return chunk

    def processSelectors(self, fitsHeader: dict, selection: str) -> str:
        """ """
        nameChunk = ""
        fitsKeywords = self.fitsHeaderKeywords[selection]
        for fitsKey in fitsKeywords:
            if fitsKey not in fitsHeader:
                continue
            nameChunk = self.convertHeaderEntry(entry=fitsHeader[fitsKey], fitsKey=fitsKey)
            break
        return nameChunk

    def renameFile(self, fileName: Path) -> None:
        """ """
        with fits.open(name=fileName) as fd:
            fitsHeader = fd[0].header
            newObjectName = self.ui.newObjectName.text().upper()
            if newObjectName:
                newFileName = newObjectName
            else:
                newFileName = fitsHeader.get("OBJECT", "UNKNOWN").upper()

            for _, selector in self.selectorsDropDowns.items():
                selection = selector.currentText()
                chunk = self.processSelectors(fitsHeader, selection)
                if chunk:
                    newFileName += f"_{chunk}"
            newFileName = (self.renameDir / newFileName).with_suffix(".fits")
            fileName.rename(newFileName)

    def renameRunGUI(self) -> None:
        """ """
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
        """ """
        folder = self.ui.renameDir.text()
        self.renameDir = self.mainW.openDir(self.mainW, "Choose Input Dir", folder)
        self.ui.renameDir.setText(str(self.renameDir))
        self.ui.renameProgress.setValue(0)
