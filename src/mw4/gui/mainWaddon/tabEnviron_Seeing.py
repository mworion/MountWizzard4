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
import webbrowser
from mw4.gui.styles.colors import colors
from mw4.gui.utilities.qtHelpers import clickable, svg2pixmap
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTransform
from PySide6.QtWidgets import QLabel, QTableWidgetItem
from typing import Any


class EnvironSeeing:
    VerticalListEntries = [
        "Date [dd mon]",
        "Hour [hh:mm]",
        "High clouds  [%]",
        "Mid clouds  [%]",
        "Low clouds [%]",
        "Seeing [arcsec]",
        "Seeing index 1",
        "Seeing index 2",
        "Ground Temp [°C]",
        "Humidity [%]",
        "Bad Layers Top [km]",
        "Bad Layers Bot [km]",
        "Bad Layers [K/100m]",
        "Jet stream [m/s]",
    ]
    DataFields = [
        "time",
        "time",
        "high_clouds",
        "mid_clouds",
        "low_clouds",
        "seeing_arcsec",
        "seeing1",
        "seeing2",
        "temperature",
        "relative_humidity",
        "badlayer_top",
        "badlayer_bottom",
        "badlayer_gradient",
        "jetstream",
    ]

    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.seeingEnabled: bool = False

        signals = self.app.dReg["seeingWeather"].signals
        signals.deviceDisconnected.connect(self.clearSeeingEntries)
        signals.deviceConnected.connect(self.prepareSeeingTable)

        self.ui.unitTimeUTC.toggled.connect(self.updateSeeingEntries)
        self.app.dReg["seeingWeather"].signals.update.connect(self.prepareSeeingTable)
        clickable(self.ui.seeingIcon).connect(self.openWeb)
        self.app.colorChange.connect(self.updateSeeingEntries)
        self.app.update30m.connect(self.updateSeeingEntries)

    def setupIcons(self) -> None:
        pixmap = svg2pixmap("assets/icon/meteoblue.svg", "#124673")
        pixmap = pixmap.transformed(QTransform().rotate(-90))
        pixmap = pixmap.scaled(37, 128, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.seeingIcon.setPixmap(pixmap)
        self.ui.seeingIcon.setVisible(False)
        self.ui.seeing.setVisible(False)

    def addSkyfieldTimeObject(self, data: dict) -> None:
        ts = self.app.dReg["mount"].obsSite.ts
        data["time"] = []

        for date, hour in zip(data["date"], data["hour"]):
            y, m, d = date.split("-")
            data["time"].append(ts.utc(int(y), int(m), int(d), hour, 0, 0))

    def applyColumnStyle(
        self,
        item: QTableWidgetItem,
        j: int,
        field: str,
        data: dict,
        i: int,
        colorPrim: str,
        colorQuar: str,
        colorTer: str,
    ) -> str:
        t = f"{data[field][i]}"
        if j == 0:
            t = self.mainW.convertTime(data[field][i], "%d%b")
        elif j == 1:
            t = self.mainW.convertTime(data[field][i], "%H:00")
        elif j in [2, 3, 4]:
            color = self.mainW.calcHexColor(colorPrim, data[field][i] / 100)
            item.setBackground(QColor(color))
            item.setForeground(QColor(colorTer))
        elif j in [6]:
            color = self.mainW.calcHexColor(data["seeing1_color"][i], 0.8)
            item.setBackground(QColor(color))
            item.setForeground(QColor(colorQuar))
        elif j in [7]:
            color = self.mainW.calcHexColor(data["seeing2_color"][i], 0.8)
            item.setBackground(QColor(color))
            item.setForeground(QColor(colorQuar))
        elif j in [10, 11]:
            val = float("0" + data[field][i]) / 1000
            t = f"{val:1.1f}"
        return t

    def buildSeeingItem(
        self,
        j: int,
        field: str,
        data: dict,
        i: int,
        colorPrim: str,
        colorQuar: str,
        colorTer: str,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        item.setForeground(QColor(self.mainW.M_PRIM))
        t = self.applyColumnStyle(item, j, field, data, i, colorPrim, colorQuar, colorTer)
        item.setText(t)
        return item

    def markActualColumn(self, item: QTableWidgetItem, data: dict, i: int) -> int:
        item.setForeground(QColor(self.mainW.M_PINK))
        val = data["seeing_arcsec"][i]
        self.ui.limitForecast.setText(f"{val}")
        val = self.app.dReg["seeingWeather"].data["meta"]["last_model_update"]
        self.ui.limitForecastDate.setText(f"{val}")
        return i

    def updateSeeingEntries(self) -> None:
        if "hourly" not in self.app.dReg["seeingWeather"].data:
            return
        self.ui.seeingGroup.setTitle("Seeing data " + self.mainW.timeZoneString())
        ts = self.app.dReg["mount"].obsSite.ts
        colorPrim = colors["M_PRIM"][0]
        colorQuar = colors["M_BACK"][0]
        colorTer = colors["M_TER"][0]
        seeTab = self.ui.seeing
        data = self.app.dReg["seeingWeather"].data["hourly"]
        self.addSkyfieldTimeObject(data)
        columnCenter = 1
        for i in range(0, 96):
            isActual = abs(data["time"][i] - ts.now()) < 1 / 48
            for j, field in enumerate(self.DataFields):
                item = self.buildSeeingItem(j, field, data, i, colorPrim, colorQuar, colorTer)
                if isActual:
                    columnCenter = self.markActualColumn(item, data, i)
                seeTab.setItem(j, i, item)
        seeTab.selectColumn(columnCenter + 10)

    def clearSeeingEntries(self) -> None:
        self.ui.seeing.clear()
        self.ui.seeingIcon.setVisible(False)
        self.ui.seeing.setVisible(False)
        self.seeingEnabled = False

    def enableSeeingEntries(self) -> None:
        self.ui.seeingIcon.setVisible(self.seeingEnabled)
        self.ui.seeing.setVisible(self.seeingEnabled)

    def prepareSeeingTable(self) -> None:
        self.seeingEnabled = True
        self.enableSeeingEntries()
        self.ui.seeing.setRowCount(14)
        self.ui.seeing.setColumnCount(96)
        self.ui.seeing.setCornerButtonEnabled(False)
        self.ui.seeing.setVerticalHeaderLabels(self.VerticalListEntries)
        self.ui.seeing.setCornerWidget(QLabel())
        self.ui.seeing.verticalHeader().setDefaultSectionSize(18)
        self.updateSeeingEntries()
        self.ui.seeing.resizeColumnsToContents()

    def openWeb(self) -> None:
        url = "https://www.meteoblue.com/de/wetter/outdoorsports/seeing"
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "Environment", "Browser failed")
        else:
            self.msg.emit(0, "System", "Environment", "Meteoblue opened")
