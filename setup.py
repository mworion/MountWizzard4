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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
from setuptools import setup
from pathlib import Path
import platform

releaseNotes = """
- add: game controller interface for mount and dome
- add: all charts could be zoomed and panned
- add: measure: window has max 5 charts now (from 3)
- add: measure: more values (time delta, focus, etc)
- add: almanac now supports UTC / local time
- add: almanac support set/rise times moon
- add: analyse: charts could show horizon and values for each point 
- add: analyse: alt / az charts with iso error curves 
- add: sound for connection lost and sat start tracking
- add: model points: multiple variants for edit and move points
- add: model points: set dither on celestial paths
- add: model points: generate from actual used mount model
- add: model points: existing model files could be loaded
- add: hemisphere: show actual model error in background
- add: hemisphere: edit horizon model much more efficient
- add: dome: control azimuth move CW / CCW for INDI
- add: satellites: all time values could be UTC or local time now
- add: image: photometry functions (aberration, roundness, etc.)
- add: image: solve and center to image
- improve: complete rework of charting: performance and functions
- improve: cleanup of gui
- improve: iers download messages
- improve: optimized DSO path generation (always fit, less params)
- improve: moved to actual jpl kernel de440.bsp for ephemeris calcs
- imporove: simplify and rearrange GUI
- remove: matplotlib usage and replace with pyqtgraph
- remove: stacking in imageW as it was never used
- fix: device selection tab was not properly positioned in device popup
 """

with open('notes.txt', 'w') as f:
    f.writelines(releaseNotes)

setup(
    name='mountwizzard4',
    version='3.0.0b0',
    packages=[
        'mw4',
        'mw4.base',
        'mw4.gui',
        'mw4.indibase',
        'mw4.gui.extWindows',
        'mw4.gui.extWindows.hemisphere',
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
        'mw4.logic.photometry',
        'mw4.logic.powerswitch',
        'mw4.logic.remote',
        'mw4.logic.telescope',
        'mw4.logic.keypad',
        'mw4.mountcontrol',
        'mw4.resource',
    ],
    python_requires='>=3.7.0, <3.11',
    install_requires=[
        'numpy==1.22.4',
        'pillow==9.1.0',
        'pyqtgraph==0.12.4',
        'pyerfa==2.0.0.1',
        'python-dateutil==2.8.2',
        'astropy==5.1',
        'astroquery==0.4.6',
        'scipy==1.8.1',
        'sep==1.2.1',
        'requests==2.27.1',
        'requests_toolbelt==0.9.1',
        'skyfield==1.42',
        'sgp4==2.21',
        'qimage2ndarray==1.9.0',
        'importlib_metadata==4.11.4',
        'deepdiff==5.8.1',
        'wakeonlan==2.1.0',
        'pybase64==1.2.1',
        'websocket-client==1.3.2',
        'hidapi==0.11.2',
    ]
    + (['pywin32==304'] if platform.system() == "Windows" else [])
    + (['pywinauto==0.6.8'] if platform.system() == "Windows" else [])
    + (['PyQt5==5.15.6'] if platform.machine() not in ['armv7l'] else [])
    + (['PyQt3D==5.15.5'] if platform.machine() not in ['armv7l',
                                                        'aarch64'] else []),
    keywords=['5.15.6'],
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='Michael Wuertenberger',
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
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'Operating System :: Microsoft :: Windows :: Windows 10',
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
