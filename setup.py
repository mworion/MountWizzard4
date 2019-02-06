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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
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
        'mw4.base',
        'mw4.modeldata',
        'mw4.environ',
        'mw4.gui',
        'mw4.gui.media',
        'mw4.gui.widgets',
        'mw4.gui.mainWmixin',
        'mw4.relay',
        'mw4.test',
    ],
    python_requires='~=3.6.7',
    install_requires=[
        'PyQt5==5.11.3',
        'matplotlib==3.0.2',
        'requests==2.21.0',
        'numpy==1.15.4',
        'requests_toolbelt==0.8.0',
        'skyfield==1.10',
        'mountcontrol>=0.62',
        'indibase>=0.3',
        'astropy==3.1',
        'wakeonlan==1.1.6',
        'mountcontrol==0.1',
        'indibase==0.41',
    ],
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='tooling for a 10micron mount',
)
