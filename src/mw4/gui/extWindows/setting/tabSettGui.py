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
import pylnk3
from importlib.resources import files
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.qtHelpers import svg2pixmap
from pathlib import Path
from typing import Any


class SettGui:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui

    def initConfig(self) -> None:
        config = self.app.config.get("SettingGui", {})
        colSet = config.get("colorSet", 0)
        self.ui.scale.setValue(config.get("scale", 1))
        self.ui.dpi.setValue(config.get("dpi", 96))
        self.ui.colorSet.setCurrentIndex(colSet)
        self.ui.transparency.setValue(config.get("transparency", 1))
        cfg = self.app.dReg["hidController"].instance.config
        self.ui.hidDome.setChecked(cfg.dome)
        self.ui.hidAltAz.setChecked(cfg.moveAltAz)
        self.ui.hidRaDec.setChecked(cfg.moveRaDec)
        self.ui.hidTracking.setChecked(cfg.tracking)
        self.ui.hidParkStop.setChecked(cfg.parkStop)
        self.ui.hidDome.clicked.connect(self.storeConfig)
        self.ui.hidParkStop.clicked.connect(self.storeConfig)
        self.ui.hidAltAz.clicked.connect(self.storeConfig)
        self.ui.hidRaDec.clicked.connect(self.storeConfig)
        self.ui.hidTracking.clicked.connect(self.storeConfig)
        self.ui.colorSet.currentIndexChanged.connect(self.updateColorSet)
        self.ui.transparency.valueChanged.connect(self.updateColorSet)
        self.ui.writeLinuxConfig.clicked.connect(self.runLinuxConfig)
        self.ui.writeLinuxConfig.setEnabled(platform.system() == "Linux")
        self.ui.writeWindowsConfig.clicked.connect(self.runWindowsConfig)
        self.ui.writeWindowsConfig.setEnabled(platform.system() == "Windows")

    def storeConfig(self) -> None:
        self.app.config["SettingGui"] = {}
        config = self.app.config["SettingGui"]
        config["colorSet"] = self.ui.colorSet.currentIndex()
        config["transparency"] = self.ui.transparency.value()
        config["scale"] = self.ui.scale.value()
        config["dpi"] = self.ui.dpi.value()
        cfg = self.app.dReg["hidController"].instance.config
        cfg.dome = self.ui.hidDome.isChecked()
        cfg.moveAltAz = self.ui.hidAltAz.isChecked()
        cfg.moveRaDec = self.ui.hidRaDec.isChecked()
        cfg.parkStop = self.ui.hidParkStop.isChecked()
        cfg.tracking = self.ui.hidTracking.isChecked()
        self.app.hidModeChanged.emit()

    def setupIcons(self) -> None:
        pixmap = svg2pixmap("assets/icon/controllerNew.svg", self.parentW.M_PRIM)
        self.ui.controllerOverview.setPixmap(pixmap)

    def updateColorSet(self) -> None:
        Styles.colorSet = self.ui.colorSet.currentIndex()
        Styles.transparency = self.ui.transparency.value()
        self.parentW.setStyleSheet(self.parentW.mw4Style)
        self.setupIcons()
        self.app.colorChange.emit()

    def writeLinuxDesktopData(self) -> None:
        localPathApplications = Path.home() / ".local/share/applications/MountWizzard4.desktop"
        workdir = self.app.mwGlob["workDir"]
        iconPath = files("mw4").joinpath("assets/icon/mw4.png")
        dpi = self.ui.dpi.value()
        scale = self.ui.scale.value()

        with open(localPathApplications, "w") as f:
            f.write("[Desktop Entry]\n")
            f.write("Type=Application\n")
            f.write("Terminal=false\n")
            f.write(f"Exec=uv --directory {str(workdir)} run mw4  -d {dpi} -s {scale}\n")
            f.write("Name=MountWizzard4\n")
            f.write("Comment=MountWizzard4 Tooling\n")
            f.write(f"Icon={str(iconPath)}\n")

    @staticmethod
    def setPermissionLinuxDesktopData() -> None:
        localPathApplications = Path.home() / ".local/share/applications/MountWizzard4.desktop"
        localPathApplications.chmod(0o755)

    def runLinuxConfig(self) -> None:
        self.writeLinuxDesktopData()
        self.setPermissionLinuxDesktopData()

    def runWindowsConfig(self) -> None:
        localPathApplications = Path.home() / ".local\\bin\\uv.exe"
        iconPath = files("mw4").joinpath("assets/icon/mw4.ico")
        workdir = self.app.mwGlob["workDir"]
        linkFile = workdir / "MountWizzard.lnk"
        linkFile.unlink(missing_ok=True)
        dpi = self.ui.dpi.value()
        scale = self.ui.scale.value()

        pylnk3.for_file(
            target_file=str(localPathApplications),
            arguments=f"run mw4 -d {dpi} -s {scale}",
            lnk_name="MountWizzard4.lnk",
            description="MountWizzard4 Shortcut",
            work_dir=str(workdir),
            icon_file=str(iconPath),
        )
