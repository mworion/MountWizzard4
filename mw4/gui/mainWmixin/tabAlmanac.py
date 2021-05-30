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
# written in python3, (c) 2019-2021 by mworion
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
        self.dark = None
        self.thread = None

        self.colors = {
            0: {'text': self.COLOR_BLUE4,
                'plot': self.M_BLUE4,
                },
            1: {'text': self.COLOR_BLUE3,
                'plot': self.M_BLUE3,
                },
            2: {'text': self.COLOR_BLUE2,
                'plot': self.M_BLUE2,
                },
            3: {'text': self.COLOR_BLUE1,
                'plot': self.M_BLUE1,
                },
            4: {'text': self.COLOR_WHITE1,
                'plot': self.M_BACK,
                },
        }

        self.app.start1s.connect(self.searchTwilightList)
        self.app.start3s.connect(self.searchTwilightPlot)
        self.app.update30m.connect(self.updateMoonPhase)
        self.ui.almanacCivil.setStyleSheet(self.BACK_BLUE1)
        self.ui.almanacNautical.setStyleSheet(self.BACK_BLUE2)
        self.ui.almanacAstronomical.setStyleSheet(self.BACK_BLUE3)
        self.ui.almanacDark.setStyleSheet(self.BACK_BLUE4)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        self.updateMoonPhase()
        self.lunarNodes()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if self.thread:
            self.thread.join()
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
            hour = int(ti.astimezone(tzlocal()).strftime('%H'))
            minute = int(ti.astimezone(tzlocal()).strftime('%M'))
            y = (hour + 12 + minute / 60) % 24
            day = round(ti.tt + 0.5, 0)
            axe.bar(day, height=24 - y, bottom=y, width=1,
                    color=self.colors[event]['plot'])

        x = [midLim - 1, midLim - 1, midLim + 1, midLim + 1]
        y = [0, 24, 24, 0]
        axe.fill(x, y, self.M_GREY, alpha=0.5)
        if self.closing:
            return False
        axe.figure.canvas.draw()
        return True

    def displayTwilightData(self, timeEvents, events):
        """
        :param timeEvents:
        :param events:
        :return:
        """
        text = ''
        self.ui.twilightEvents.clear()

        for timeEvent, event in zip(timeEvents, events):
            self.ui.twilightEvents.setTextColor(self.colors[event]['text'])
            text += f'{timeEvent.astimezone(tzlocal()).strftime("%H:%M:%S")} '
            text += f'{almanac.TWILIGHTS[event]}'
            self.ui.twilightEvents.insertPlainText(text)
            text = '\n'
        return True

    def calcTwilightData(self, ts, location, timeWindow=0):
        """
        :param ts:
        :param location:
        :param timeWindow:
        :return:
        """
        timeJD = self.app.mount.obsSite.timeJD
        t0 = ts.tt_jd(int(timeJD.tt) - timeWindow)
        t1 = ts.tt_jd(int(timeJD.tt) + timeWindow + 1)

        f = almanac.dark_twilight_day(self.app.ephemeris, location)
        f.step_days = 0.04
        timeEvents, events = almanac.find_discrete(t0, t1, f)
        return timeEvents, events

    def searchTwilightWorker(self, ts, location, timeWindow):
        """
        :param ts:
        :param location:
        :param timeWindow:
        :return: true for test purpose
        """
        t, e = self.calcTwilightData(ts, location, timeWindow)
        return ts, t, e

    def searchTwilightPlot(self):
        """
        :return: true for test purpose
        """
        location = self.app.mount.obsSite.location
        if location is None:
            return False

        ts = self.app.mount.obsSite.ts
        worker = Worker(self.searchTwilightWorker, ts, location, 182)
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
        t, e = self.calcTwilightData(ts, location)
        self.displayTwilightData(t, e)
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

        e = earth.at(self.app.mount.obsSite.timeJD)
        _, sunLon, _ = e.observe(sun).apparent().ecliptic_latlon()
        _, moonLon, _ = e.observe(moon).apparent().ecliptic_latlon()

        mpIllumination = almanac.fraction_illuminated(self.app.ephemeris,
                                                      'moon', now)
        mpDegree = (moonLon.degrees - sunLon.degrees) % 360.0
        mpPercent = mpDegree / 360

        return mpIllumination, mpDegree, mpPercent

    @staticmethod
    def generateMoonMask(width, height, mpDegree):
        """
        :param width:
        :param height:
        :param mpDegree:
        :return:
        """
        moonMask = QPixmap(width, height)
        maskPainter = QPainter(moonMask)
        maskPainter.setBrush(Qt.SolidPattern)
        maskPainter.setBrush(QColor(255, 255, 255))
        maskPainter.setPen(QPen(QColor(255, 255, 255)))
        maskPainter.drawRect(0, 0, width, height)

        if 0 <= mpDegree <= 90:
            maskPainter.setBrush(QColor(48, 48, 48))
            maskPainter.drawPie(0, 0, width, height, 90 * 16, 180 * 16)

            r = np.cos(np.radians(mpDegree)) * width / 2
            maskPainter.setBrush(QColor(48, 48, 48))
            maskPainter.setPen(QPen(QColor(48, 48, 48)))
            maskPainter.drawEllipse(QPointF(width / 2, height / 2), r, height / 2)

        elif 90 < mpDegree <= 180:
            maskPainter.setBrush(QColor(48, 48, 48))
            maskPainter.drawPie(0, 0, width, height, 90 * 16, 180 * 16)

            r = - np.cos(np.radians(mpDegree)) * width / 2
            maskPainter.setBrush(QColor(255, 255, 255))
            maskPainter.setPen(QPen(QColor(255, 255, 255)))
            maskPainter.drawEllipse(QPointF(width / 2, height / 2), r, height / 2)

        elif 180 < mpDegree <= 270:
            maskPainter.setBrush(QColor(48, 48, 48))
            maskPainter.drawPie(0, 0, width, height, - 90 * 16, 180 * 16)

            r = - np.cos(np.radians(mpDegree)) * width / 2
            maskPainter.setBrush(QColor(255, 255, 255))
            maskPainter.setPen(QPen(QColor(255, 255, 255)))
            maskPainter.drawEllipse(QPointF(width / 2, height / 2), r, height / 2)

        else:
            maskPainter.setBrush(QColor(48, 48, 48))
            maskPainter.drawPie(0, 0, width, height, -90 * 16, 180 * 16)

            r = np.cos(np.radians(mpDegree)) * width / 2
            maskPainter.setPen(QPen(QColor(48, 48, 48)))
            maskPainter.setBrush(QColor(48, 48, 48))
            maskPainter.drawEllipse(QPointF(width / 2, height / 2), r, height / 2)

        maskPainter.end()
        return moonMask

    def updateMoonPhase(self):
        """
        It will also write some description for the moon phase. In addition I
        will show an image of the moon showing the moon phase as picture.

        :return: true for test purpose
        """
        mpIllumination, mpDegree, mpPercent = self.calcMoonPhase()

        self.ui.moonPhaseIllumination.setText(f'{mpIllumination * 100:3.2f}')
        self.ui.moonPhasePercent.setText(f'{100* mpPercent:3.0f}')
        self.ui.moonPhaseDegree.setText(f'{mpDegree:3.0f}')

        for phase in self.phasesText:
            if int(mpPercent * 100) not in range(*self.phasesText[phase]['range']):
                continue
            self.ui.moonPhaseText.setText(phase)

        width = self.ui.moonPic.width()
        height = self.ui.moonPic.height()
        moon = QPixmap(':/pics/moon.png').scaled(width, height)
        moonMask = self.generateMoonMask(width, height, mpDegree)
        moonPhase = QPainter(moon)
        moonPhase.setCompositionMode(QPainter.CompositionMode_Multiply)
        moonPhase.drawPixmap(0, 0, moonMask)
        moonPhase.end()
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
        text = 'descending' if y[0] else 'ascending'
        self.ui.lunarNodes.setText(f'{text}')

        return True
