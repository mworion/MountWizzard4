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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import


class AlignMount(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.lastModelType = ''

        ms = self.app.mount.signals
        ms.alignDone.connect(self.updateAlignGUI)
        ms.alignDone.connect(self.updateTurnKnobsGUI)

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

    def updateAlignGUI(self, model):
        """
        updateAlignGUI shows the data which is received through the getain command. this is
        mainly polar and ortho errors as well as basic model data.

        :param model:
        :return:    True if ok for testing
        """

        if model.numberStars is not None:
            text = str(model.numberStars)
        else:
            text = '-'
        self.ui.numberStars.setText(text)
        self.ui.numberStars1.setText(text)

        if model.terms is not None:
            text = str(model.terms)
        else:
            text = '-'
        self.ui.terms.setText(text)

        if model.errorRMS is not None:
            text = str(model.errorRMS)
        else:
            text = '-'
        self.ui.errorRMS.setText(text)
        self.ui.errorRMS1.setText(text)

        if model.positionAngle is not None:
            text = f'{model.positionAngle.degrees:5.1f}'
        else:
            text = '-'
        self.ui.positionAngle.setText(text)

        if model.polarError is not None:
            text = f'{model.polarError.degrees * 60:5.2f}'
        else:
            text = '-'
        self.ui.polarError.setText(text)

        if model.orthoError is not None:
            text = f'{model.orthoError.degrees * 60:5.2f}'
        else:
            text = '-'
        self.ui.orthoError.setText(text)

        if model.azimuthError is not None:
            text = f'{model.azimuthError.degrees:5.1f}'
        else:
            text = '-'
        self.ui.azimuthError.setText(text)

        if model.altitudeError is not None:
            text = f'{model.altitudeError.degrees:5.1f}'
        else:
            text = '-'
        self.ui.altitudeError.setText(text)

        return True

    def updateTurnKnobsGUI(self, model):
        """
        updateTurnKnobsGUI shows the data which is received through the getain command.
        this is mainly polar and ortho errors as well as basic model data.

        :param model:
        :return:    True if ok for testing
        """

        if model.azimuthTurns is not None:
            if model.azimuthTurns > 0:
                text = '{0:3.1f} revs left'.format(abs(model.azimuthTurns))
            else:
                text = '{0:3.1f} revs right'.format(abs(model.azimuthTurns))
        else:
            text = '-'
        self.ui.azimuthTurns.setText(text)

        if model.altitudeTurns is not None:
            if model.altitudeTurns > 0:
                text = '{0:3.1f} revs down'.format(abs(model.altitudeTurns))
            else:
                text = '{0:3.1f} revs up'.format(abs(model.altitudeTurns))
        else:
            text = '-'
        self.ui.altitudeTurns.setText(text)

        return True
