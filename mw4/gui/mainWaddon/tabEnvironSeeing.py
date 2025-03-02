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
import webbrowser

# external packages
from PySide6.QtCore import Qt, QObject
from PySide6.QtGui import QColor, QTransform
from PySide6.QtWidgets import QTableWidgetItem

# local import
from gui.styles.colors import colors
from gui.utilities.toolsQtWidget import clickable


class EnvironSeeing(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.seeingEnabled = False
        signals = self.app.seeingWeather.signals
        signals.deviceDisconnected.connect(self.clearSeeingEntries)
        signals = self.app.seeingWeather.signals
        signals.deviceConnected.connect(self.prepareSeeingTable)

        self.ui.unitTimeUTC.toggled.connect(self.updateSeeingEntries)
        self.app.seeingWeather.signals.update.connect(self.prepareSeeingTable)
        clickable(self.ui.meteoblueIcon).connect(self.openMeteoblue)
        self.app.start3s.connect(self.enableSeeingEntries)
        self.app.colorChange.connect(self.prepareSeeingTable)
        self.app.update30m.connect(self.updateSeeingEntries)

    def setupIcons(self) -> None:
        """ """
        pixmap = self.mainW.svg2pixmap(":/icon/meteoblue.svg", "#124673")
        pixmap = pixmap.transformed(QTransform().rotate(-90))
        pixmap = pixmap.scaled(37, 128, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.meteoblueIcon.setPixmap(pixmap)
        self.ui.meteoblueIcon.setVisible(False)
        self.ui.meteoblueSeeing.setVisible(False)

    def addSkyfieldTimeObject(self, data: dict) -> None:
        """ """
        ts = self.app.mount.obsSite.ts
        data["time"] = []

        for date, hour in zip(data["date"], data["hour"]):
            y, m, d = date.split("-")
            data["time"].append(ts.utc(int(y), int(m), int(d), hour, 0, 0))

    def updateSeeingEntries(self) -> None:
        """ """
        if "hourly" not in self.app.seeingWeather.data:
            return

        self.ui.seeingGroup.setTitle("Seeing data " + self.mainW.timeZoneString())
        ts = self.app.mount.obsSite.ts
        fields = [
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
        colorPrim = colors["M_PRIM"][0]
        colorQuar = colors["M_BACK"][0]
        colorTer = colors["M_TER"][0]
        seeTab = self.ui.meteoblueSeeing
        data = self.app.seeingWeather.data["hourly"]
        self.addSkyfieldTimeObject(data)

        for i in range(0, 96):
            isActual = abs(data["time"][i] - ts.now()) < 1 / 48

            for j, field in enumerate(fields):
                t = f"{data[field][i]}"
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                item.setForeground(QColor(self.mainW.M_PRIM))

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

                if isActual:
                    item.setForeground(QColor(self.mainW.M_PINK))
                    val = data["seeing_arcsec"][i]
                    self.ui.limitForecast.setText(f"{val}")
                    val = self.app.seeingWeather.data["meta"]["last_model_update"]
                    self.ui.limitForecastDate.setText(f"{val}")
                    columnCenter = i
                else:
                    columnCenter = 1

                item.setText(t)
                seeTab.setItem(j, i, item)

        seeTab.selectColumn(columnCenter + 10)

    def clearSeeingEntries(self) -> None:
        """ """
        self.ui.meteoblueSeeing.clear()
        self.ui.meteoblueIcon.setVisible(False)
        self.ui.meteoblueSeeing.setVisible(False)
        self.seeingEnabled = False

    def enableSeeingEntries(self) -> None:
        """ """
        if not self.seeingEnabled:
            return

        self.ui.meteoblueIcon.setVisible(True)
        self.ui.meteoblueSeeing.setVisible(True)

    def prepareSeeingTable(self) -> None:
        """ """
        vl = [
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
            "",
        ]

        self.seeingEnabled = True
        self.enableSeeingEntries()
        seeTab = self.ui.meteoblueSeeing
        if platform.system() == "Darwin":
            seeTab.setRowCount(15)
        else:
            seeTab.setRowCount(14)
        seeTab.setColumnCount(96)
        seeTab.setVerticalHeaderLabels(vl)
        seeTab.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        seeTab.verticalHeader().setDefaultSectionSize(18)
        self.updateSeeingEntries()
        seeTab.resizeColumnsToContents()

    def openMeteoblue(self) -> None:
        """ """
        url = "https://www.meteoblue.com/de/wetter/outdoorsports/seeing"
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "Environment", "Browser failed")
        else:
            self.msg.emit(0, "System", "Environment", "Meteoblue opened")
