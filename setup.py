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
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
from setuptools import setup
from mw4.mainApp import MountWizzard4

setup(
    name='mw4',
    version=MountWizzard4.version,
    packages=[
        'mw4',
        'mw4.astrometry',
        'mw4.base',
        'mw4.dome',
        'mw4.environment',
        'mw4.gui',
        'mw4.gui.media',
        'mw4.gui.widgets',
        'mw4.gui.mainWmixin',
        'mw4.imaging',
        'mw4.modeldata',
        'mw4.powerswitch',
        'mw4.remote',
    ],
    python_requires='>=3.7.2',
    install_requires=[
        'PyQt5==5.12.2',
        'matplotlib==3.1',
        'requests==2.22.0',
        'requests_toolbelt==0.9.1',
        'numpy==1.16.4',
        'skyfield==1.10',
        'mountcontrol>=0.100',
        'astropy==3.1.2',
        'wakeonlan==1.1.6',
        'indibase>=0.100',
    ],
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='tooling for a 10micron mount',
)
