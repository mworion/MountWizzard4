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

        self.twilight = self.embedMatplot(self.ui.twilight)
        self.searchTwilight()
        self.drawTwilight()

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

        ts = self.app.mount.obsSite.ts
        location = self.app.mount.obsSite.location
        eph = self.app.planets

        t0 = ts.utc(2020, 1, 1, 0)
        t1 = ts.utc(2020, 12, 31, 24)
        f = almanac.dark_twilight_day(eph, location)
        times, events = almanac.find_discrete(t0, t1, f)

        colors = [self.M_BLUE,
                  self.M_YELLOW,
                  self.M_RED,
                  self.M_WHITE,
                  self.M_GREEN]

        for ti, event in zip(times, events):
            hour = int(ti.utc_datetime().strftime('%H'))
            minute = int(ti.utc_datetime().strftime('%M'))

            y = (hour + minute / 60 + 12) % 24
            day = int(ti.utc_datetime().strftime('%j'))

            axe.plot(day, y, marker='.', linestyle=None, color=colors[event])

        axe.figure.canvas.draw()

        return True

    def searchTwilight(self):
        """

        :return: true for test purpose
        """
        return True
