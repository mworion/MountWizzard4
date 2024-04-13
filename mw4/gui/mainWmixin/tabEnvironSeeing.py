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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import platform
import webbrowser

# external packages
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableWidgetItem

# local import


class EnvironSeeing:
    """
    """

    def __init__(self):
        self.seeingEnabled = False

        signals = self.app.seeingWeather.signals
        signals.deviceDisconnected.connect(self.clearSeeingEntries)
        signals = self.app.seeingWeather.signals
        signals.deviceConnected.connect(self.prepareSeeingTable)

        self.ui.unitTimeUTC.toggled.connect(self.updateSeeingEntries)
        self.app.seeingWeather.signals.update.connect(self.prepareSeeingTable)
        self.clickable(self.ui.meteoblueIcon).connect(self.openMeteoblue)
        self.app.start3s.connect(self.enableSeeingEntries)
        self.app.colorChange.connect(self.prepareSeeingTable)
        self.app.update30m.connect(self.updateSeeingEntries)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        return True

    def addSkyfieldTimeObject(self, data):
        """
        :param data:
        :return:
        """
        ts = self.app.mount.obsSite.ts
        data['time'] = []

        for date, hour in zip(data['date'], data['hour']):
            y, m, d = date.split('-')
            data['time'].append(ts.utc(int(y), int(m), int(d), hour, 0, 0))
        return True

    def updateSeeingEntries(self):
        """
        :return:
        """
        if 'hourly' not in self.app.seeingWeather.data:
            return False

        self.ui.seeingGroup.setTitle('Seeing data ' + self.timeZoneString())
        ts = self.app.mount.obsSite.ts
        fields = ['time', 'time', 'high_clouds', 'mid_clouds', 'low_clouds',
                  'seeing_arcsec', 'seeing1', 'seeing2', 'temperature',
                  'relative_humidity', 'badlayer_top', 'badlayer_bottom',
                  'badlayer_gradient', 'jetstream']
        colorMain = self.cs['M_BLUE'][0]
        colorBlack = self.cs['M_BLACK'][0]
        colorWhite = self.cs['M_WHITE'][0]
        seeTab = self.ui.meteoblueSeeing
        data = self.app.seeingWeather.data['hourly']
        self.addSkyfieldTimeObject(data)

        for i in range(0, 96):
            isActual = abs(data['time'][i] - ts.now()) < 1 / 48

            for j, field in enumerate(fields):
                t = f'{data[field][i]}'
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                item.setForeground(QColor(self.M_BLUE))

                if j == 0:
                    t = self.convertTime(data[field][i], '%d%b')
                elif j == 1:
                    t = self.convertTime(data[field][i], '%H:00')
                elif j in [2, 3, 4]:
                    color = self.calcHexColor(colorMain, data[field][i] / 100)
                    item.setBackground(QColor(color))
                    item.setForeground(QColor(colorWhite))
                elif j in [6]:
                    color = self.calcHexColor(data['seeing1_color'][i], 0.8)
                    item.setBackground(QColor(color))
                    item.setForeground(QColor(colorBlack))
                elif j in [7]:
                    color = self.calcHexColor(data['seeing2_color'][i], 0.8)
                    item.setBackground(QColor(color))
                    item.setForeground(QColor(colorBlack))
                elif j in [10, 11]:
                    val = float('0' + data[field][i]) / 1000
                    t = f'{val:1.1f}'

                if isActual:
                    item.setForeground(QColor(self.M_PINK))
                    val = data['seeing_arcsec'][i]
                    self.ui.limitForecast.setText(f'{val}')
                    val = self.app.seeingWeather.data['meta']['last_model_update']
                    self.ui.limitForecastDate.setText(f'{val}')
                    columnCenter = i
                else:
                    columnCenter = 1

                item.setText(t)
                seeTab.setItem(j, i, item)

        seeTab.selectColumn(columnCenter + 10)
        return True

    def clearSeeingEntries(self):
        """
        :return:
        """
        self.ui.meteoblueSeeing.clear()
        self.ui.meteoblueIcon.setVisible(False)
        self.ui.meteoblueSeeing.setVisible(False)
        self.seeingEnabled = False
        return True

    def enableSeeingEntries(self):
        """
        :return:
        """
        if not self.seeingEnabled:
            return False

        self.ui.meteoblueIcon.setVisible(True)
        self.ui.meteoblueSeeing.setVisible(True)
        return True

    def prepareSeeingTable(self):
        """
        :return:
        """
        vl = ['Date [dd mon]',
              'Hour [hh:mm]',
              'High clouds  [%]',
              'Mid clouds  [%]',
              'Low clouds [%]',
              'Seeing [arcsec]',
              'Seeing index 1',
              'Seeing index 2',
              'Ground Temp [°C]',
              'Humidity [%]',
              'Bad Layers Top [km]',
              'Bad Layers Bot [km]',
              'Bad Layers [K/100m]',
              'Jet stream [m/s]',
              '',
              ]

        self.seeingEnabled = True
        self.enableSeeingEntries()
        seeTab = self.ui.meteoblueSeeing
        if platform.system() == 'Darwin':
            seeTab.setRowCount(15)
        else:
            seeTab.setRowCount(14)
        seeTab.setColumnCount(96)
        seeTab.setVerticalHeaderLabels(vl)
        seeTab.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        seeTab.verticalHeader().setDefaultSectionSize(18)
        self.updateSeeingEntries()
        seeTab.resizeColumnsToContents()
        return True

    def openMeteoblue(self):
        """
        :return:
        """
        url = 'https://www.meteoblue.com/de/wetter/outdoorsports/seeing'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Environment', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Environment', 'Meteoblue opened')
        return True
