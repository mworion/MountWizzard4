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
# GUI with PyQT5 for python3
#
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
from setuptools import setup
from pathlib import Path
import platform

releaseNotes = """
- add: hemisphere window: help for choosing the right star for polar alignment
- add: hemisphere terrain adjust for altitude of image beside azimuth
- add: angular error ra / dec axis in measurement
- add: device connection similar for ASCOM and ALPACA devices
- add: extended satellite search and filter capabilities (spreadsheet style)
- add: estimation of satellite apparent magnitude
- add: extended satellite tracking and tuning capabilities
- add: enabling loading a custom satellite TLE data file
- add: command window for manual mount commands
- add: sorting for minimal dome slew in build point selection
- add: setting prediction time of almanac (shorter reduces cpu load)
- add: providing 3 different color schemes
- add: virtual keypad available for RPi 3/4 users now
- improve: check if satellite data is valid (avoid error messages)
- improve: better hints when using 10micron updater
- improve: simplified signals generation
- improve: analyse window plots
- improve: rewrite alpaca / ascom interface
- improve: gui for running functions
- improve: test coverage
- remove: push time from mount to computer: in reliable and unstable
- fix: segfault in qt5lib on ubuntu
 """

with open('notes.txt', 'w') as f:
    f.writelines(releaseNotes)

setup(
    name='mountwizzard4',
    version='2.1.0',
    packages=[
        'mw4',
        'mw4.base',
        'mw4.gui',
        'mw4.indibase',
        'mw4.gui.extWindows',
        'mw4.gui.extWindows.simulator',
        'mw4.gui.mainWmixin',
        'mw4.gui.mainWindow',
        'mw4.gui.utilities',
        'mw4.gui.widgets',
        'mw4.logic.astrometry',
        'mw4.logic.automation',
        'mw4.logic.camera',
        'mw4.logic.cover',
        'mw4.logic.databaseProcessing',
        'mw4.logic.dome',
        'mw4.logic.environment',
        'mw4.logic.filter',
        'mw4.logic.focuser',
        'mw4.logic.measure',
        'mw4.logic.modeldata',
        'mw4.logic.powerswitch',
        'mw4.logic.remote',
        'mw4.logic.telescope',
        'mw4.logic.keypad',
        'mw4.mountcontrol',
        'mw4.resource',
    ],
    python_requires='>=3.7.0, <3.10',
    install_requires=[
        'numpy==1.21.2',
        'pillow==8.3.1',
        'matplotlib==3.4.2',
        'pyerfa==2.0.0',
        'astropy==4.3.1',
        'scipy==1.7.1',
        'sep==1.2.0',
        'requests==2.26.0',
        'requests_toolbelt==0.9.1',
        'skyfield==1.39',
        'sgp4==2.20',
        'qimage2ndarray==1.8.3',
        'importlib_metadata==4.6.4',
        'deepdiff==5.5.0',
        'colour_demosaicing==0.1.6',
        'wakeonlan==2.0.1',
        'pybase64==1.2.0',
        'websocket-client==1.2.1',
    ]
    + (['pywin32==301'] if platform.system() == "Windows" else [])
    + (['pywinauto==0.6.8'] if platform.system() == "Windows" else [])
    + (['PyQt5==5.15.4'] if platform.machine() not in ['armv7l'] else [])
    + (['PyQt3D==5.15.4'] if platform.machine() not in ['armv7l',
                                                        'aarch64'] else []),
    keywords=['5.15.4'],
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='mworion',
    author_email='michael@wuertenberger.org',
    description='Tool for managing 10micron mounts',
    long_description=Path("README.rst").read_text(encoding="utf-8"),
    long_description_content_type="text/x-rst",
    project_urls={
        'Documentation': 'https://mountwizzard4.readthedocs.io',
        'Source Code': 'https://github.com/mworion/mountwizzard4',
        'Bug Tracker': 'https://github.com/mworion/mountwizzard4/issues',
        'Discussions': 'https://github.com/mworion/MountWizzard4/discussions',
        'Channel': 'https://www.youtube.com/user/orion49m/featured',
        'Forum': 'https://www.10micron.eu/forum/',
    },
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: MacOS X',
        'Environment :: Other Environment',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Astronomy',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Natural Language :: German',
        'Topic :: Documentation :: Sphinx',
    ]
)
