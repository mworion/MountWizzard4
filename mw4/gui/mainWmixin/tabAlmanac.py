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
from PyQt5.QtGui import QPixmap
from skyfield import almanac
import numpy as np

# local import


class Almanac(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadPool for managing async
    processing if needed.
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

        self.civilT1 = list()
        self.nauticalT1 = list()
        self.astronomicalT1 = list()
        self.darkT1 = list()
        self.civilT2 = list()
        self.nauticalT2 = list()
        self.astronomicalT2 = list()
        self.darkT2 = list()
        self.thread = None

        self.moonPhasePercent = 0

        self.app.mount.signals.locationDone.connect(self.searchTwilight)
        self.app.mount.signals.locationDone.connect(self.displayTwilightData)
        self.ui.checkTimezoneUTC.clicked.connect(self.displayTwilightData)
        self.ui.checkTimezoneLocal.clicked.connect(self.displayTwilightData)

        self.app.update1s.connect(self.updateMoonPhase)
        self.lunarNodes()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        self.ui.checkTimezoneUTC.setChecked(config.get('checkTimezoneUTC', True))
        self.ui.checkTimezoneLocal.setChecked(config.get('checkTimezoneLocal', False))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        config['checkTimezoneUTC'] = self.ui.checkTimezoneUTC.isChecked()
        config['checkTimezoneLocal'] = self.ui.checkTimezoneLocal.isChecked()

        if self.thread:
            self.thread.join()

        return True

    def drawTwilight(self, minDay, maxDay):
        """

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

        val = self.civilT1 + list(reversed(self.civilT2))
        x = [x[0].tt for x in val]
        y = [x[1] for x in val]
        axe.fill(x, y, self.M_BLUE1)
        axe.plot(x, y, self.M_BLUE1)

        val = self.nauticalT1 + list(reversed(self.nauticalT2))
        x = [x[0].tt for x in val]
        y = [x[1] for x in val]
        axe.fill(x, y, self.M_BLUE2)
        axe.plot(x, y, self.M_GREY)

        val = self.astronomicalT1 + list(reversed(self.astronomicalT2))
        x = [x[0].tt for x in val]
        y = [x[1] for x in val]
        axe.fill(x, y, self.M_BLUE3)
        axe.plot(x, y, self.M_GREY)

        val = self.darkT1 + list(reversed(self.darkT2))
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

        :return: true for test purpose
        """

        ts = self.app.mount.obsSite.ts
        timeJD = self.app.mount.obsSite.timeJD
        location = self.app.mount.obsSite.location

        if location is None:
            return False

        t0 = ts.tt_jd(int(timeJD.tt) - 182)
        t1 = ts.tt_jd(int(timeJD.tt) + 182)

        f = almanac.dark_twilight_day(self.app.ephermeris, location)
        t, e = almanac.find_discrete(t0, t1, f)

        self.civilT1 = list()
        self.nauticalT1 = list()
        self.astronomicalT1 = list()
        self.darkT1 = list()
        self.civilT2 = list()
        self.nauticalT2 = list()
        self.astronomicalT2 = list()
        self.darkT2 = list()

        stat = 4
        minDay = None
        for ti, event in zip(t, e):
            hour = int(ti.utc_datetime().strftime('%H'))
            minute = int(ti.utc_datetime().strftime('%M'))

            y = (hour + 12 + minute / 60) % 24
            day = ti

            if minDay is None:
                minDay = day

            if stat == 4 and event == 3:
                self.civilT1.append([day, y])
            elif stat == 3 and event == 2:
                self.nauticalT1.append([day, y])
            elif stat == 2 and event == 1:
                self.astronomicalT1.append([day, y])
            elif stat == 1 and event == 0:
                self.darkT1.append([day, y])
            elif stat == 0 and event == 1:
                self.darkT2.append([day, y])
            elif stat == 1 and event == 2:
                self.astronomicalT2.append([day, y])
            elif stat == 2 and event == 3:
                self.nauticalT2.append([day, y])
            elif stat == 3 and event == 4:
                self.civilT2.append([day, y])
            stat = event

        maxDay = day

        self.drawTwilight(minDay, maxDay)

        return

    def searchTwilight(self):
        """

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

        f = almanac.dark_twilight_day(self.app.ephermeris, location)
        t, e = almanac.find_discrete(t0, t1, f)

        if self.ui.checkTimezoneUTC.isChecked():
            tz = tzutc()
        else:
            tz = tzlocal()

        text = ''
        self.ui.twilightEvents.clear()

        for timeE, event in zip(t, e):
            text += f'{timeE.astimezone(tz).strftime("%H:%M:%S")} '
            text += f'{almanac.TWILIGHTS[event]}\n'

        text = text.rstrip('\n')
        self.ui.twilightEvents.insertPlainText(text)

        return True

    def updateMoonPhase(self):
        """

        :return: true for test purpose
        """
        phasesText = {
            'New moon': {
                'range': (0, 1),
                'pic': ':/moon/new.png',
            },
            'Waxing crescent': {
                'range': (1, 23),
                'pic': ':/moon/waxing_crescent.png',
            },
            'First Quarter': {
                'range': (23, 27),
                'pic': ':/moon/first_quarter.png',
            },
            'Waxing Gibbous': {
                'range': (27, 48),
                'pic': ':/moon/waxing_gibbous.png',
            },
            'Full moon': {
                'range': (48, 52),
                'pic': ':/moon/full.png',
            },
            'Waning Gibbous': {
                'range': (52, 73),
                'pic': ':/moon/waning_gibbous.png',
            },
            'Third quarter': {
                'range': (73, 77),
                'pic': ':/moon/third_quarter.png',
            },
            'Waning crescent': {
                'range': (77, 99),
                'pic': ':/moon/waning_crescent.png',
            },
            'New moon ': {
                'range': (99, 100),
                'pic': ':/moon/new.png',
            },
        }

        # todo: is the calculation of the moon phase better separate ?
        sun = self.app.ephermeris['sun']
        moon = self.app.ephermeris['moon']
        earth = self.app.ephermeris['earth']

        e = earth.at(self.app.mount.obsSite.timeJD)
        _, sunLon, _ = e.observe(sun).apparent().ecliptic_latlon()
        _, moonLon, _ = e.observe(moon).apparent().ecliptic_latlon()

        now = self.app.mount.obsSite.ts.now()
        moonPhaseIllumination = almanac.fraction_illuminated(self.app.ephermeris, 'moon', now)
        moonPhaseDegree = (moonLon.degrees - sunLon.degrees) % 360.0
        moonPhasePercent = moonPhaseDegree / 360

        self.ui.moonPhaseIllumination.setText(f'{moonPhaseIllumination * 100:3.2f}')
        self.ui.moonPhasePercent.setText(f'{100* moonPhasePercent:3.0f}')
        self.ui.moonPhaseDegree.setText(f'{moonPhaseDegree:3.0f}')

        for phase in phasesText:
            if int(moonPhasePercent * 100) not in range(*phasesText[phase]['range']):
                continue
            self.ui.moonPhaseText.setText(phase)
            pixmap = QPixmap(phasesText[phase]['pic']).scaled(60, 60)
            self.ui.moonPic.setPixmap(pixmap)

        """
        # forecast 48 hours
        ts = self.app.mount.obsSite.ts
        t0 = ts.utc(2019, 12, 1, 5)
        t1 = ts.utc(2019, 12, 31, 5)
        e = self.app.ephermeris
        loc = self.app.mount.obsSite.location
        t, y = almanac.find_discrete(t0, t1, almanac.dark_twilight_day(e, loc))
        for ti, yi in zip(t, y):
            print(yi, ti.utc_iso())
        """

        return True

    def lunarNodes(self):
        """

        :return: true for test purpose
        """
        ts = self.app.mount.obsSite.ts
        timeJD = self.app.mount.obsSite.timeJD

        t0 = ts.tt_jd(int(timeJD.tt))
        t1 = ts.tt_jd(int(timeJD.tt) + 29)
        t, y = almanac.find_discrete(t0, t1, almanac.moon_nodes(self.app.ephermeris))

        self.ui.lunarNodes.setText(f'{almanac.MOON_NODES[y[0]]}')

        return True
