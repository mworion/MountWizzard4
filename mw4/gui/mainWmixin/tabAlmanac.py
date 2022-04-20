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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from dateutil.tz import tzlocal

# external packages
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QApplication
from skyfield import almanac
from skyfield.trigonometry import position_angle_of
import numpy as np

# local import
from base.tpool import Worker


class Almanac:
    """
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

    def __init__(self):
        self.civil = None
        self.nautical = None
        self.astronomical = None
        self.twilightTime = None
        self.twilightEvents = None
        self.colors = None
        self.setColors()
        self.app.start1s.connect(self.searchTwilightList)
        self.app.start5s.connect(self.searchTwilightPlot)
        self.app.update1s.connect(self.updateMoonPhase)
        self.app.colorChange.connect(self.colorChangeAlmanac)
        self.ui.almanacDark.clicked.connect(self.updateMoonPhase)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.almanacPrediction.setCurrentIndex(config.get('almanacPrediction', 0))
        self.ui.almanacPrediction.currentIndexChanged.connect(self.searchTwilightPlot)
        self.updateMoonPhase()
        self.lunarNodes()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['almanacPrediction'] = self.ui.almanacPrediction.currentIndex()
        return True

    def setColors(self):
        """
        :return:
        """
        self.ui.almanacCivil.setStyleSheet(f'background-color: {self.M_BLUE1};')
        self.ui.almanacNautical.setStyleSheet(f'background-color: {self.M_BLUE2};')
        self.ui.almanacAstronomical.setStyleSheet(f'background-color: {self.M_BLUE3};')
        self.ui.almanacDark.setStyleSheet(f'background-color: {self.M_BLUE4};')
        self.colors = [self.M_BLUE4, self.M_BLUE3, self.M_BLUE2, self.M_BLUE1,
                       self.M_BACK]
        return True

    def colorChangeAlmanac(self):
        """
        :return:
        """
        self.setColors()
        self.searchTwilightPlot()
        self.updateMoonPhase()
        return True

    def plotTwilightData(self, result):
        """
        :param result:
        :return: true for test purpose
        """
        ts, t, e = result
        minLim = int(t[0].tt) + 1
        maxLim = int(t[-1].tt) - 1
        midLim = minLim + (maxLim - minLim) / 2

        axe, fig = self.generateFlat(widget=self.twilight)
        yTicks = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
        yLabels = ['12', '14', '16', '18', '20', '22', '24',
                   '02', '04', '06', '08', '10', '12']
        axe.set_yticks(yTicks)
        axe.set_yticklabels(yLabels, fontsize=10)
        xTicks = np.arange(minLim, maxLim, (maxLim - minLim) / 11)
        xLabels = ts.tt_jd(xTicks).utc_strftime('%d%b')
        xLabels[0] = ''
        axe.set_xlim(minLim, maxLim)
        axe.set_xticks(xTicks)
        axe.set_xticklabels(xLabels, fontsize=10)
        axe.grid(color=self.M_GREY, alpha=0.5)
        axe.set_ylim(0, 24)

        for ti, event in zip(t, e):
            QApplication.processEvents()
            if self.closing:
                break
            hour = int(ti.astimezone(tzlocal()).strftime('%H'))
            minute = int(ti.astimezone(tzlocal()).strftime('%M'))
            y = (hour + 12 + minute / 60) % 24
            day = round(ti.tt + 0.5, 0)
            axe.bar(day, height=24 - y, bottom=y, width=1,
                    color=self.colors[event])
        else:
            x = [midLim - 1, midLim - 1, midLim + 1, midLim + 1]
            y = [0, 24, 24, 0]
            axe.fill(x, y, self.M_GREY, alpha=0.5)
            axe.figure.canvas.draw()
            return True
        return False

    def displayTwilightData(self, timeEvents, events):
        """
        :param timeEvents:
        :param events:
        :return:
        """
        text = ''
        self.ui.twilightEvents.clear()

        for timeEvent, event in zip(timeEvents, events):
            text += f'{timeEvent.astimezone(tzlocal()).strftime("%H:%M:%S")} '
            text += f'{almanac.TWILIGHTS[event]}'
            self.ui.twilightEvents.insertPlainText(text)
            text = '\n'
        return True

    def calcTwilightData(self, ts, location, tWinL=0, tWinH=0):
        """
        :param ts:
        :param location:
        :param tWinL:
        :param tWinH:
        :return:
        """
        timeJD = self.app.mount.obsSite.timeJD
        t0 = ts.tt_jd(int(timeJD.tt) - tWinL)
        t1 = ts.tt_jd(int(timeJD.tt) + tWinH + 1)

        f = almanac.dark_twilight_day(self.app.ephemeris, location)
        twilightTime, twilightEvents = almanac.find_discrete(t0, t1, f)
        return twilightTime, twilightEvents

    def searchTwilightWorker(self, ts, location, timeWindow):
        """
        :param ts:
        :param location:
        :param timeWindow:
        :return: true for test purpose
        """
        t, e = self.calcTwilightData(ts, location,
                                     tWinL=timeWindow,
                                     tWinH=timeWindow)
        return ts, t, e

    def searchTwilightPlot(self):
        """
        :return: true for test purpose
        """
        timeWindowParam = [17, 32, 47, 92, 182]
        location = self.app.mount.obsSite.location
        if location is None:
            return False

        index = self.ui.almanacPrediction.currentIndex()
        text = self.ui.almanacPrediction.currentText()
        timeWindow = timeWindowParam[index]
        self.ui.almanacGroup.setTitle(f'Twilight passes for: {text}')

        ts = self.app.mount.obsSite.ts
        worker = Worker(self.searchTwilightWorker, ts, location, timeWindow)
        worker.signals.result.connect(self.plotTwilightData)
        self.threadPool.start(worker)
        return True

    def searchTwilightList(self):
        """
        :return: true for test purpose
        """
        location = self.app.mount.obsSite.location
        if location is None:
            return False

        ts = self.app.mount.obsSite.ts
        result = self.calcTwilightData(ts, location, tWinL=0, tWinH=1)
        self.twilightTime, self.twilightEvents = result
        self.displayTwilightData(self.twilightTime[:8], self.twilightEvents[:8])
        return True

    def calcMoonPhase(self):
        """
        calcMoonPhase searches for moon events, moon phase and illumination
        percentage.

        :return: fraction of illumination, degree phase and percent phase
        """
        sun = self.app.ephemeris['sun']
        moon = self.app.ephemeris['moon']
        earth = self.app.ephemeris['earth']
        now = self.app.mount.obsSite.ts.now()
        loc = self.app.mount.obsSite.location + earth

        e = earth.at(self.app.mount.obsSite.timeJD)
        _, sunLon, _ = e.observe(sun).apparent().ecliptic_latlon()
        _, moonLon, _ = e.observe(moon).apparent().ecliptic_latlon()

        mpIllumination = almanac.fraction_illuminated(self.app.ephemeris,
                                                      'moon', now)
        mpDegree = (moonLon.degrees - sunLon.degrees) % 360.0
        mpPercent = mpDegree / 360

        locObserver = loc.at(self.app.mount.obsSite.timeJD)
        moonApparent = locObserver.observe(moon).apparent()
        sunApparent = locObserver.observe(sun).apparent()
        moonAngle = position_angle_of(moonApparent.altaz(), sunApparent.altaz())

        return mpIllumination, mpDegree, mpPercent, moonAngle

    def generateMoonMask(self, pixmap, mpDegree):
        """
        :param pixmap:
        :param mpDegree:
        :return:
        """
        colCover = QColor(self.M_BACK)
        colFree = QColor('transparent')
        colFrame = QColor(self.M_GREY1)
        colRed = QColor(self.M_RED)

        penCov = QPen(colCover, 0)
        penFree = QPen(colFree, 0)
        penFrame = QPen(colFrame, 3)
        penRed = QPen(colRed, 3)

        height = pixmap.height()
        width = pixmap.width()
        h2 = height / 2
        w2 = width / 2

        moonMask = QPixmap(width, height)
        moonMask.fill(QColor('transparent'))

        maskPainter = QPainter(moonMask)
        maskPainter.setBrush(Qt.SolidPattern)
        maskPainter.setBrush(colFree)
        maskPainter.setPen(penFrame)

        if 0 <= mpDegree <= 90:
            # left half covered
            maskPainter.setBrush(colCover)
            maskPainter.drawPie(0, 0, width, height, 90 * 16, 180 * 16)

            # right half opens up
            r = np.cos(np.radians(mpDegree)) * w2
            maskPainter.setBrush(colCover)
            maskPainter.setPen(penCov)
            maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        elif 90 < mpDegree <= 180:
            maskPainter.setBrush(colCover)
            maskPainter.drawPie(0, 0, width, height, 90 * 16, 180 * 16)

            maskPainter.setCompositionMode(QPainter.CompositionMode_Clear)
            r = np.cos(np.radians(mpDegree)) * w2
            maskPainter.setBrush(colFree)
            maskPainter.setPen(colFree)
            maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        elif 180 < mpDegree <= 270:
            maskPainter.setBrush(colCover)
            maskPainter.drawPie(0, 0, width, height, - 90 * 16, 180 * 16)

            maskPainter.setCompositionMode(QPainter.CompositionMode_Clear)
            r = np.cos(np.radians(mpDegree)) * w2
            maskPainter.setBrush(colFree)
            maskPainter.setPen(penFree)
            maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        else:
            maskPainter.setBrush(colCover)
            maskPainter.drawPie(0, 0, width, height, -90 * 16, 180 * 16)

            r = np.cos(np.radians(mpDegree)) * w2
            maskPainter.setPen(penCov)
            maskPainter.setBrush(colCover)
            maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        maskPainter.end()
        return moonMask

    def updateMoonPhase(self):
        """
        It will also write some description for the moon phase. In addition I
        will show an image of the moon showing the moon phase as picture.

        :return: true for test purpose
        """
        mpIllumination, mpDegree, mpPercent, mAngle = self.calcMoonPhase()
        self.ui.moonPhaseIllumination.setText(f'{mpIllumination * 100:3.2f}')
        self.ui.moonPhasePercent.setText(f'{100* mpPercent:3.0f}')
        self.ui.moonPhaseDegree.setText(f'{mpDegree:3.0f}')

        for phase in self.phasesText:
            if int(mpPercent * 100) not in range(*self.phasesText[phase]['range']):
                continue
            self.ui.moonPhaseText.setText(phase)

        moon = QPixmap(':/pics/moon.png')
        moonMask = self.generateMoonMask(moon, mpDegree)

        m = QPainter(moon)
        m.setCompositionMode(QPainter.CompositionMode_SourceOver)
        m.drawPixmap(0, 0, moonMask)
        m.end()

        width = self.ui.moonPic.width()
        height = self.ui.moonPic.height()
        self.ui.moonPic.setPixmap(moon.scaled(width, height))
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
        text = 'descending' if y[0] else 'ascending'
        self.ui.lunarNodes.setText(f'{text}')
        return True
