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

# external packages
from skyfield import almanac

# local import
from mw4.base.tpool import Worker


class EnvironHelpers(object):
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

        self.daysTwilight = list()
        self.timeTwilight = list()
        self.colorTwilight = list()

        self.twilight = self.embedMatplot(self.ui.twilight)
        self.app.mount.signals.locationDone.connect(self.searchTwilightWorker)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']

        return True

    def drawTwilight(self):
        """

        :return: true for test purpose
        """
        axe, fig = self.generateFlat(widget=self.twilight,
                                     title='Twilight')

        axe.set_xlabel('Date',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Time [h]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        axe.set_ylim(0, 24)

        colors = [self.M_BLUE,
                  self.M_YELLOW,
                  self.M_RED,
                  self.M_WHITE,
                  self.M_GREEN]

        for day, time, color in zip(self.daysTwilight,
                                    self.timeTwilight,
                                    self.colorTwilight):
            axe.plot(day,
                     time,
                     marker='.',
                     color=colors[color])

        axe.figure.canvas.draw()

        return True

    def searchTwilightWorker(self):
        """

        :return: true for test purpose
        """

        obs = self.app.mount.obsSite
        location = self.app.mount.obsSite.location
        eph = self.app.planets

        t0 = obs.ts.tt_jd(int(obs.timeJD.tt) - 54.5)
        t1 = obs.ts.tt_jd(int(obs.timeJD.tt) + 55.5)

        f = almanac.dark_twilight_day(eph, location)

        t, e = almanac.find_discrete(t0, t1, f)

        self.daysTwilight = list()
        self.timeTwilight = list()
        self.colorTwilight = list()

        for ti, event in zip(t, e):
            hour = int(ti.utc_datetime().strftime('%H'))
            minute = int(ti.utc_datetime().strftime('%M'))

            y = (hour - 12 + minute / 60) % 24
            day = int(ti.utc_datetime().strftime('%j'))
            self.daysTwilight.append(day)
            self.timeTwilight.append(y)
            self.colorTwilight.append(event)

        self.drawTwilight()
        return True

    def searchTwilight(self):
        """

        :return: true for test purpose
        """

        worker = Worker(self.searchTwilightWorker)
        worker.signals.finished.connect(self.drawTwilight)
        self.threadPool.start(worker)

        return True
