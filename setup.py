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
    name='MountWizzard4',
    version=MountWizzard4.version,
    packages=[
        'mw4',
    ],
    python_requires='>=3.7.2',
    install_requires=[
        'PyQt5==5.12',
        'matplotlib==3.0.3',
        'requests==2.21.0',
        'requests_toolbelt==0.9.1',
        'numpy==1.16.2',
        'skyfield==1.10',
        'mountcontrol>=0.82',
        'astropy==3.1.2',
        'wakeonlan==1.1.6',
        'indibase>=0.51',
    ],
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='tooling for a 10micron mount',
)
