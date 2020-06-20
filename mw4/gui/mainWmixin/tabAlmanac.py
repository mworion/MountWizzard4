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

        self.civilT1 = list()
        self.nauticalT1 = list()
        self.astronomicalT1 = list()
        self.darkT1 = list()
        self.civilT2 = list()
        self.nauticalT2 = list()
        self.astronomicalT2 = list()
        self.darkT2 = list()

        self.app.mount.signals.locationDone.connect(self.displayTwilightData)
        self.ui.checkTimezoneUTC.clicked.connect(self.displayTwilightData)
        self.ui.checkTimezoneLocal.clicked.connect(self.displayTwilightData)
        self.ui.isOnline.stateChanged.connect(self.updateOnlineTwilight)

        self.displayTwilightData()
        self.app.update30m.connect(self.updateMoonPhase)
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
        self.updateMoonPhase()
        self.updateOnlineTwilight()

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

        return True

    @staticmethod
    def processOnlineTwilightImage(image=None):
        """
        processClearOutsideImage takes the image, split it and puts the image
        to the Gui. for the transformation qimage2ndarray is used because of the speed
        for the calculations. dim is a factor which reduces the lightness of the overall
        image

        :param image:
        :return: success
        """
        dim = 0.85

        image.convertToFormat(PyQt5.QtGui.QImage.Format_RGB32)
        imageBase = image.copy(10, 50, 732, 735)

        imgArr = qimage2ndarray.rgb_view(imageBase)
        imgArr = np.delete(imgArr, range(620, 700), axis=0)
        imgArr = np.delete(imgArr, range(0, 80), axis=0)
        imageBase = qimage2ndarray.array2qimage(dim * imgArr)

        pixmap = PyQt5.QtGui.QPixmap().fromImage(imageBase)
        pixmap = pixmap.scaledToHeight(396)

        return pixmap

    def updateOnlineTwilightImage(self, data=None):
        """
        updateOnlineTwilightImage takes the returned data from a web fetch and makes an image
        out of it

        :param data:
        :return: success
        """

        if data is None:
            return False

        image = PyQt5.QtGui.QImage()

        if not hasattr(data, 'content'):
            return False
        if not isinstance(data.content, bytes):
            return False

        image.loadFromData(data.content)

        pixmapBase = self.processOnlineTwilightImage(image=image)
        self.ui.onlineTwilight.setPixmap(pixmapBase)

        return True

    def getOnlineTwilight(self, url=''):
        """
        getOnlineTwilight initiates the worker thread to get the web data fetched

        :param url:
        :return:
        """
        worker = Worker(self.getWebDataWorker, url)
        worker.signals.result.connect(self.updateOnlineTwilightImage)
        self.threadPool.start(worker)

    def updateOnlineTwilight(self):
        """
        updateOnlineTwilight downloads the actual clear outside image and displays it in
        environment tab. it checks first if online is set, otherwise not download will take
        place. it will be updated every 30 minutes.

        confirmation for using the service :

        Grant replied Aug 5, 10:01am
        Hi Michael,
        No problem at all embedding the forecast as shown in your image :-)
        We appreciate the support.
        Kindest Regards,
        Grant

        :return: success
        """

        if not self.ui.isOnline.isChecked():
            pixmap = PyQt5.QtGui.QPixmap(':/pics/offlineMode.png')
            self.ui.onlineTwilight.setPixmap(pixmap)
            return False

        # prepare coordinates for website
        loc = self.app.mount.obsSite.location
        lat = loc.latitude.degrees
        lon = loc.longitude.degrees

        webSite = 'http://clearoutside.com/annual_darkness_image/'
        url = f'{webSite}{lat:4.2f}/{lon:4.2f}/annual_darkness.png'
        self.getOnlineTwilight(url=url)

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
