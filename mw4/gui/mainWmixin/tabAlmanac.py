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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import threading
from dateutil.tz import tzlocal, tzutc

# external packages
import PyQt5.QtCore
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPointF
from skyfield import almanac
import numpy as np
import qimage2ndarray

# local import
from mw4.base.tpool import Worker


class Almanac(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadPool for managing async
    processing if needed.
    """

    phasesText = {
        'New moon': {
            'range': (0, 1),
        },
        'Waxing crescent': {
            'range': (1, 23),
        },
        'First Quarter': {
            'range': (23, 27),
        },
        'Waxing Gibbous': {
            'range': (27, 48),
        },
        'Full moon': {
            'range': (48, 52),
        },
        'Waning Gibbous': {
            'range': (52, 73),
        },
        'Third quarter': {
            'range': (73, 77),
        },
        'Waning crescent': {
            'range': (77, 99),
        },
        'New moon ': {
            'range': (99, 100),
        },
    }

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

        self.civil = None
        self.nautical = None
        self.astronomical = None
        self.dark = None

        self.thread = None

        self.app.mount.signals.locationDone.connect(self.searchTwilight)
        self.app.mount.signals.locationDone.connect(self.displayTwilightData)

        self.app.update30m.connect(self.updateMoonPhase)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        # config = self.app.config['mainW']

        self.updateMoonPhase()
        self.searchTwilight()
        self.displayTwilightData()
        self.lunarNodes()

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        # config = self.app.config['mainW']

        if self.thread:
            self.thread.join()

        return True

    def drawTwilight(self, minDay, maxDay):
        """
        draw Twilight takes the different stats for each day during a year (half a year to the past,
        half year to the future) and draws the chart for UTC time only.

        :return: true for test purpose
        """

        if minDay is None or maxDay is None:
            return False

        ts = self.app.mount.obsSite.ts
        minLim = int(minDay.tt) + 1
        maxLim = int(maxDay.tt) - 1
        midLim = minLim + (maxLim - minLim) / 2

        axe, fig = self.generateFlat(widget=self.twilight)

        yTicks = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
        yLabels = ['12', '14', '16', '18', '20', '22', '24',
                   '02', '04', '06', '08', '10', '12']

        axe.set_yticks(yTicks)
        axe.set_yticklabels(yLabels)

        xTicks = np.arange(minLim, maxLim, (maxLim - minLim) / 11)
        xLabels = ts.tt_jd(xTicks).utc_strftime('%m-%d')
        xLabels[0] = ''
        axe.set_xlim(minLim, maxLim)

        axe.set_xticks(xTicks)
        axe.set_xticklabels(xLabels)

        axe.grid(color=self.M_GREY, alpha=0.5)
        axe.set_ylim(0, 24)

        for i in self.civil:
            val = self.civil[i]
            if not len(val):
                break
            val.append(val[0])
            x = [x[0].tt for x in val]
            y = [x[1] for x in val]
            axe.fill(x, y, self.M_BLUE1)
            axe.plot(x, y, self.M_BLUE1)

        for i in self.nautical:
            val = self.nautical[i]
            if not len(val):
                break
            val.append(val[0])
            x = [x[0].tt for x in val]
            y = [x[1] for x in val]
            axe.fill(x, y, self.M_BLUE2)
            axe.plot(x, y, self.M_GREY)

        for i in self.astronomical:
            val = self.astronomical[i]
            if not len(val):
                break
            val.append(val[0])
            x = [x[0].tt for x in val]
            y = [x[1] for x in val]
            axe.fill(x, y, self.M_BLUE3)
            axe.plot(x, y, self.M_GREY)

        for i in self.dark:
            val = self.dark[i]
            if not len(val):
                break
            val.append(val[0])
            x = [x[0].tt for x in val]
            y = [x[1] for x in val]
            axe.fill(x, y, self.M_BLUE4)
            axe.plot(x, y, self.M_GREY)

        x = [midLim - 2, midLim - 2, midLim + 2, midLim + 2]
        y = [0, 24, 24, 0]
        axe.fill(x, y, self.M_GREY, alpha=0.5)

        # draw legend
        d = 0
        x = [minLim + 5 + d, minLim + 5 + d, minLim + 85 + d,
             minLim + 85 + d, minLim + 5 + d]
        y = [22.5, 23.5, 23.5, 22.5, 22.5]
        axe.fill(x, y, self.M_BLUE1)
        axe.plot(x, y, self.M_GREY)
        axe.annotate('Civil', (minLim + 12 + d, 22.75),
                     color=self.M_WHITE, weight='bold')

        d = 90
        x = [minLim + 5 + d, minLim + 5 + d, minLim + 85 + d,
             minLim + 85 + d, minLim + 5 + d]
        axe.fill(x, y, self.M_BLUE2)
        axe.plot(x, y, self.M_GREY)
        axe.annotate('Nautical', (minLim + 12 + d, 22.75),
                     color=self.M_WHITE, weight='bold')

        d = 180
        x = [minLim + 5 + d, minLim + 5 + d, minLim + 85 + d,
             minLim + 85 + d, minLim + 5 + d]
        axe.fill(x, y, self.M_BLUE3)
        axe.plot(x, y, self.M_GREY)
        axe.annotate('Astronomical', (minLim + 12 + d, 22.75),
                     color=self.M_WHITE, weight='bold')

        d = 270
        x = [minLim + 5 + d, minLim + 5 + d, minLim + 85 + d,
             minLim + 85 + d, minLim + 5 + d]
        axe.fill(x, y, self.M_BLUE4)
        axe.plot(x, y, self.M_GREY)
        axe.annotate('Dark', (minLim + 12 + d, 22.75),
                     color=self.M_WHITE, weight='bold')

        x = [midLim - 20, midLim - 20, midLim + 20, midLim + 20, midLim - 20]
        y = [0.5, 1.5, 1.5, 0.5, 0.5]
        axe.fill(x, y, self.M_GREY, alpha=0.5)
        axe.plot(x, y, self.M_GREY)
        axe.annotate('Today', (midLim - 12, 0.75),
                     color=self.M_WHITE, weight='bold')

        axe.figure.canvas.draw()

        return True

    def searchTwilightWorker(self):
        """
        searchTwilightWorker is the worker method which does the search for twilight events
        during one year with actual day as middle point. As this search take some time and
        the gui should be still responsive, this method will run in a separate thread.

        :return: true for test purpose
        """

        ts = self.app.mount.obsSite.ts
        timeJD = self.app.mount.obsSite.timeJD
        location = self.app.mount.obsSite.location

        if location is None:
            return False

        t0 = ts.tt_jd(int(timeJD.tt) - 182)
        t1 = ts.tt_jd(int(timeJD.tt) + 182)

        f = almanac.dark_twilight_day(self.app.ephemeris, location)
        t, e = almanac.find_discrete(t0, t1, f)

        self.civil = {0: []}
        civilP = 0
        self.nautical = {0: []}
        nauticalP = 0
        self.astronomical = {0: []}
        astronomicalP = 0
        self.dark = {0: []}
        darkP = 0
        civilE = False
        nauticalE = False
        astronomicalE = False
        darkE = False

        stat = 4
        lastDay = round(t0.tt + 0.5, 0)

        minDay = None
        for ti, event in zip(t, e):
            hour = int(ti.astimezone(tzlocal()).strftime('%H'))
            minute = int(ti.astimezone(tzlocal()).strftime('%M'))

            y = (hour + 12 + minute / 60) % 24
            day = round(ti.tt + 0.5, 0)

            if minDay is None:
                minDay = ti

            if day != lastDay:
                if not civilE:
                    if len(self.civil[civilP]):
                        civilP += 1
                        self.civil[civilP] = []
                if not nauticalE:
                    if len(self.nautical[nauticalP]):
                        nauticalP += 1
                        self.nautical[nauticalP] = []
                if not astronomicalE:
                    if len(self.astronomical[astronomicalP]):
                        astronomicalP += 1
                        self.astronomical[astronomicalP] = []
                if not darkE:
                    if len(self.dark[darkP]):
                        darkP += 1
                        self.dark[darkP] = []
                lastDay = day
                civilE = False
                nauticalE = False
                astronomicalE = False
                darkE = False

            if stat == 4 and event == 3:
                self.civil[civilP].append([ti, y])
                civilE = True
            elif stat == 3 and event == 2:
                self.nautical[nauticalP].append([ti, y])
                nauticalE = True
            elif stat == 2 and event == 1:
                self.astronomical[astronomicalP].append([ti, y])
                astronomicalE = True
            elif stat == 1 and event == 0:
                self.dark[darkP].append([ti, y])
                darkE = True
            elif stat == 0 and event == 1:
                self.dark[darkP].insert(0, [ti, y])
                darkE = True
            elif stat == 1 and event == 2:
                self.astronomical[astronomicalP].insert(0, [ti, y])
                astronomicalE = True
            elif stat == 2 and event == 3:
                self.nautical[nauticalP].insert(0, [ti, y])
                nauticalE = True
            elif stat == 3 and event == 4:
                self.civil[civilP].insert(0, [ti, y])
                civilE = True

            stat = event

        maxDay = ti

        self.drawTwilight(minDay, maxDay)

        return

    def searchTwilight(self):
        """
        search twilight just starts the worker in a separate thread.

        :return: true for test purpose
        """

        self.thread = threading.Thread(target=self.searchTwilightWorker)
        self.thread.start()

        return True

    def displayTwilightData(self):
        """
        displayTwilightData populates the readable list of twilight events in the upcoming
        observation night. the user could choose the timezone local or UTC

        :return: true for test purpose
        """

        ts = self.app.mount.obsSite.ts
        timeJD = self.app.mount.obsSite.timeJD
        location = self.app.mount.obsSite.location

        if location is None:
            return False

        t0 = ts.tt_jd(int(timeJD.tt))
        t1 = ts.tt_jd(int(timeJD.tt) + 1)

        f = almanac.dark_twilight_day(self.app.ephemeris, location)
        t, e = almanac.find_discrete(t0, t1, f)

        text = ''
        self.ui.twilightEvents.clear()

        for timeE, event in zip(t, e):
            text += f'{timeE.astimezone(tzlocal()).strftime("%H:%M:%S")} '
            text += f'{almanac.TWILIGHTS[event]}\n'

        text = text.rstrip('\n')
        self.ui.twilightEvents.insertPlainText(text)

        return True

    def updateMoonPhase(self):
        """
        updateMoonPhase searches for moon events, moon phase and illumination percentage.
        It will also write some description for the moon phase. In addition I will show an
        image of the moon showing the moon phase as picture.

        :return: true for test purpose
        """

        sun = self.app.ephemeris['sun']
        moon = self.app.ephemeris['moon']
        earth = self.app.ephemeris['earth']
        now = self.app.mount.obsSite.ts.now()

        e = earth.at(self.app.mount.obsSite.timeJD)
        _, sunLon, _ = e.observe(sun).apparent().ecliptic_latlon()
        _, moonLon, _ = e.observe(moon).apparent().ecliptic_latlon()

        moonPhaseIllumination = almanac.fraction_illuminated(self.app.ephemeris, 'moon', now)
        moonPhaseDegree = (moonLon.degrees - sunLon.degrees) % 360.0
        moonPhasePercent = moonPhaseDegree / 360

        self.ui.moonPhaseIllumination.setText(f'{moonPhaseIllumination * 100:3.2f}')
        self.ui.moonPhasePercent.setText(f'{100* moonPhasePercent:3.0f}')
        self.ui.moonPhaseDegree.setText(f'{moonPhaseDegree:3.0f}')

        for phase in self.phasesText:
            if int(moonPhasePercent * 100) not in range(*self.phasesText[phase]['range']):
                continue
            self.ui.moonPhaseText.setText(phase)

        width = self.ui.moonPic.width()
        height = self.ui.moonPic.height()

        mask = QPixmap(width, height)
        maskP = QPainter(mask)
        maskP.setBrush(Qt.SolidPattern)
        maskP.setBrush(QColor(255, 255, 255))
        maskP.setPen(QPen(QColor(255, 255, 255)))
        maskP.drawRect(0, 0, width, height)

        if moonPhaseDegree <= 90:
            maskP.setBrush(QColor(48, 48, 48))
            maskP.drawPie(0, 0, width, height, 90 * 16, 180 * 16)

            r = np.cos(np.radians(moonPhaseDegree)) * width / 2
            maskP.setBrush(QColor(48, 48, 48))
            maskP.setPen(QPen(QColor(48, 48, 48)))
            maskP.drawEllipse(QPointF(width / 2, height / 2), r, height / 2)

        elif 90 < moonPhaseDegree <= 180:
            maskP.setBrush(QColor(48, 48, 48))
            maskP.drawPie(0, 0, width, height, 90 * 16, 180 * 16)

            r = - np.cos(np.radians(moonPhaseDegree)) * width / 2
            maskP.setBrush(QColor(255, 255, 255))
            maskP.setPen(QPen(QColor(255, 255, 255)))
            maskP.drawEllipse(QPointF(width / 2, height / 2), r, height / 2)

        elif 180 < moonPhaseDegree <= 270:
            maskP.setBrush(QColor(48, 48, 48))
            maskP.drawPie(0, 0, width, height, - 90 * 16, 180 * 16)

            r = - np.cos(np.radians(moonPhaseDegree)) * width / 2
            maskP.setBrush(QColor(255, 255, 255))
            maskP.setPen(QPen(QColor(255, 255, 255)))
            maskP.drawEllipse(QPointF(width / 2, height / 2), r, height / 2)

        else:
            maskP.setBrush(QColor(48, 48, 48))
            maskP.drawPie(0, 0, width, height, -90 * 16, 180 * 16)

            r = np.cos(np.radians(moonPhaseDegree)) * width / 2
            maskP.setPen(QPen(QColor(48, 48, 48)))
            maskP.setBrush(QColor(48, 48, 48))
            maskP.drawEllipse(QPointF(width / 2, height / 2), r, height / 2)

        maskP.end()

        moon = QPixmap(':/pics/moon.png').scaled(width, height)
        moonP = QPainter(moon)
        moonP.setCompositionMode(QPainter.CompositionMode_Multiply)
        moonP.drawPixmap(0, 0, mask)
        moonP.end()

        self.ui.moonPic.setPixmap(moon)

        return True

    def lunarNodes(self):
        """

        :return: true for test purpose
        """
        ts = self.app.mount.obsSite.ts
        timeJD = self.app.mount.obsSite.timeJD

        t0 = ts.tt_jd(int(timeJD.tt))
        t1 = ts.tt_jd(int(timeJD.tt) + 29)
        t, y = almanac.find_discrete(t0, t1, almanac.moon_nodes(self.app.ephemeris))

        self.ui.lunarNodes.setText(f'{almanac.MOON_NODES[y[0]]}')

        return True
