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
import copy

# external packages
from skyfield import almanac
from skyfield.api import load
from matplotlib import ticker
import matplotlib.dates as mdates

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

        self.civilT1 = list()
        self.nauticalT1 = list()
        self.astronomicalT1 = list()
        self.darkT1 = list()
        self.civilT2 = list()
        self.nauticalT2 = list()
        self.astronomicalT2 = list()
        self.darkT2 = list()

        self.twilight = self.embedMatplot(self.ui.twilight)
        # self.app.mount.signals.locationDone.connect(self.searchTwilightWorker)
        self.searchTwilight()

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

    def drawTwilight(self, dayLimits):
        """

        :return: true for test purpose
        """

        minDay, maxDay = dayLimits

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

        axe.set_yticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
        axe.set_yticklabels(['12', '14', '16', '18', '20', '22', '24',
                             '02', '04', '06', '08', '10', '12'])

        axe.grid(color=self.M_GREY, alpha=0.5)
        axe.set_ylim(0, 24)
        if minDay is not None and maxDay is not None:
            axe.set_xlim(minDay, maxDay)
        fig.autofmt_xdate()

        val = self.civilT1 + list(reversed(self.civilT2))
        x = [x[0] for x in val]
        y = [x[1] for x in val]
        axe.fill(x, y, self.M_BLUE1)
        axe.plot(x, y, self.M_BLUE1)

        val = self.nauticalT1 + list(reversed(self.nauticalT2))
        x = [x[0] for x in val]
        y = [x[1] for x in val]
        axe.fill(x, y, self.M_BLUE2)
        axe.plot(x, y, self.M_GREY)

        val = self.astronomicalT1 + list(reversed(self.astronomicalT2))
        x = [x[0] for x in val]
        y = [x[1] for x in val]
        axe.fill(x, y, self.M_BLUE3)
        axe.plot(x, y, self.M_GREY)

        val = self.darkT1 + list(reversed(self.darkT2))
        x = [x[0] for x in val]
        y = [x[1] for x in val]
        axe.fill(x, y, self.M_BLUE4)
        axe.plot(x, y, self.M_GREY)

        axe.format_xdata = mdates.DateFormatter('%m-%d')
        axe.get_xaxis().set_major_locator(ticker.MaxNLocator(nbins=12,
                                                             min_n_ticks=12,
                                                             prune='both',
                                                             ))
        axe.figure.canvas.draw()

        return True

    def searchTwilightWorker(self):
        """

        :return: true for test purpose
        """

        print('worker')
        self.ts = load.timescale(builtin=True)
        print('timescale')
        self.timeJD = copy.copy(self.app.mount.obsSite.timeJD)
        print('timeJD')
        location = copy.copy(self.app.mount.obsSite.location)
        eph = self.app.planets

        print(self.timeJD)
        print(location)

        t0 = self.ts.tt_jd(int(self.timeJD.tt) - 5)
        t1 = self.ts.tt_jd(int(self.timeJD.tt) + 5)

        f = almanac.dark_twilight_day(eph, location)
        print(f)
        t, e = almanac.find_discrete(t0, t1, f)
        print(t, e)

        self.civilT1 = list()
        self.nauticalT1 = list()
        self.astronomicalT1 = list()
        self.darkT1 = list()
        self.civilT2 = list()
        self.nauticalT2 = list()
        self.astronomicalT2 = list()
        self.darkT2 = list()

        stat = 4
        minDay = t0.utc_datetime()
        maxDay = t1.utc_datetime()
        for ti, event in zip(t, e):
            hour = int(ti.utc_datetime().strftime('%H'))
            minute = int(ti.utc_datetime().strftime('%M'))

            y = (hour + 12 + minute / 60) % 24
            day = ti.utc_datetime()

            minDay = min(minDay, day)
            maxDay = max(maxDay, day)

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

        return (minDay, maxDay)

    def searchTwilight(self):
        """

        :return: true for test purpose
        """

        worker = Worker(self.searchTwilightWorker)
        worker.signals.result.connect(self.drawTwilight)
        self.threadPool.start(worker)

        return True
