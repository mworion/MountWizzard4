#!/usr/bin/env python3
"""
Final migration script for tabSett_Dome.py with line length fixes
"""

import re
from pathlib import Path


def migrate_tabSett_Dome():
    filepath = Path("../../src/mw4/gui/mainWaddon/tabSett_Dome.py")
    content = filepath.read_text()

    # Pattern 1: Multi-line .drivers["device"]["class"] patterns
    content = re.sub(
        r'self\.app\.dReg\.drivers\["([^"]+)"\]\s*\[\s*"class"\s*\]',
        r'self.app.dReg["\1"].instance',
        content,
        flags=re.DOTALL,
    )

    # Pattern 2: Multi-line .drivers["device"]["stat"] patterns
    content = re.sub(
        r'self\.app\.dReg\.drivers\["([^"]+)"\]\s*\[\s*"stat"\s*\]',
        r'self.app.dReg["\1"].stat',
        content,
        flags=re.DOTALL,
    )

    # Pattern 3: Multi-line .drivers["device"]["deviceType"] patterns
    content = re.sub(
        r'self\.app\.dReg\.drivers\["([^"]+)"\]\s*\[\s*"deviceType"\s*\]',
        r'self.app.dReg["\1"].deviceType',
        content,
        flags=re.DOTALL,
    )

    # Now fix setUseGeometry method for line length
    old_setUseGeometry = """    def setUseGeometry(self) -> None:
        if self.ui.automaticDome.isChecked():
            self.updateDomeGeometryToGui()

        self.app.dReg["mount"].instance.geometry.domeRadius = self.ui.domeRadius.value()
        self.app.dReg["dome"].instance.radius = self.ui.domeRadius.value()
        self.app.dReg["mount"].instance.geometry.offGEM = self.ui.offGEM.value()
        self.app.dReg["mount"].instance.geometry.offLAT = self.ui.offLAT.value()"""

    new_setUseGeometry = """    def setUseGeometry(self) -> None:
        if self.ui.automaticDome.isChecked():
            self.updateDomeGeometryToGui()

        mount = self.app.dReg["mount"].instance
        dome = self.app.dReg["dome"].instance
        
        mount.geometry.domeRadius = self.ui.domeRadius.value()
        dome.radius = self.ui.domeRadius.value()
        mount.geometry.offGEM = self.ui.offGEM.value()
        mount.geometry.offLAT = self.ui.offLAT.value()"""

    content = content.replace(old_setUseGeometry, new_setUseGeometry)

    # Fix line 224 onwards (is10Micron assignment and branches)
    old_is10Micron = """        is10Micron = self.ui.use10micronDef.isChecked()
        if is10Micron:
            self.app.dReg["mount"].instance.geometry.offNorth = self.ui.domeNorthOffset.value()
            self.app.dReg["mount"].instance.geometry.offEast = self.ui.domeEastOffset.value()
            self.app.dReg["mount"].instance.geometry.offVert = self.ui.domeVerticalOffset.value()
        else:
            self.app.dReg["mount"].instance.geometry.offNorthGEM = self.ui.domeNorthOffset.value()
            self.app.dReg["mount"].instance.geometry.offEastGEM = self.ui.domeEastOffset.value()
            self.app.dReg["mount"].instance.geometry.offVertGEM = self.ui.domeVerticalOffset.value()"""

    new_is10Micron = """        is10Micron = self.ui.use10micronDef.isChecked()
        if is10Micron:
            mount.geometry.offNorth = self.ui.domeNorthOffset.value()
            mount.geometry.offEast = self.ui.domeEastOffset.value()
            mount.geometry.offVert = self.ui.domeVerticalOffset.value()
        else:
            mount.geometry.offNorthGEM = self.ui.domeNorthOffset.value()
            mount.geometry.offEastGEM = self.ui.domeEastOffset.value()
            mount.geometry.offVertGEM = self.ui.domeVerticalOffset.value()"""

    content = content.replace(old_is10Micron, new_is10Micron)

    # Fix clear Opening section
    old_clearOpening = """        clearOpening = self.ui.domeClearOpening.value()
        self.app.dReg["dome"].instance.clearOpening = clearOpening
        self.ui.domeOpeningHysteresis.setMaximum(clearOpening / 2.1)
        self.app.dReg["dome"].instance.openingHysteresis = self.ui.domeOpeningHysteresis.value()
        self.app.dReg["dome"].instance.clearanceZenith = self.ui.domeClearanceZenith.value()

        useGeometry = self.ui.useDomeGeometry.isChecked()
        self.app.dReg["dome"].instance.useGeometry = useGeometry

        useDynamicFollowing = self.ui.useDynamicFollowing.isChecked()
        self.app.dReg["dome"].instance.useDynamicFollowing = useDynamicFollowing
        self.app.dReg["dome"].instance.overshoot = self.ui.useOvershoot.isChecked()
        self.app.updateDomeSettings.emit()"""

    new_clearOpening = """        clearOpening = self.ui.domeClearOpening.value()
        dome.clearOpening = clearOpening
        self.ui.domeOpeningHysteresis.setMaximum(clearOpening / 2.1)
        dome.openingHysteresis = self.ui.domeOpeningHysteresis.value()
        dome.clearanceZenith = self.ui.domeClearanceZenith.value()

        useGeometry = self.ui.useDomeGeometry.isChecked()
        dome.useGeometry = useGeometry

        useDynamicFollowing = self.ui.useDynamicFollowing.isChecked()
        dome.useDynamicFollowing = useDynamicFollowing
        dome.overshoot = self.ui.useOvershoot.isChecked()
        self.app.updateDomeSettings.emit()"""

    content = content.replace(old_clearOpening, new_clearOpening)

    # Fix setDomeSettlingTime
    old_settlingTime = """    def setDomeSettlingTime(self) -> None:
        self.app.dReg["dome"].instance.settlingTime = self.ui.settleTimeDome.value()"""

    new_settlingTime = """    def setDomeSettlingTime(self) -> None:
        dome = self.app.dReg["dome"].instance
        dome.settlingTime = self.ui.settleTimeDome.value()"""

    content = content.replace(old_settlingTime, new_settlingTime)

    filepath.write_text(content)
    print("✓ tabSett_Dome.py successfully migrated and line length fixed")


if __name__ == "__main__":
    migrate_tabSett_Dome()
