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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
from setuptools import setup
from pathlib import Path
import platform

releaseNotes = """
- add: support for aarch64 on raspi for python 3.8 - 3.10 (needs installer 3.1)
- add: support for ASTAP new databases D50, D20, D05
- improve: speedup launch if INDI server not ready
- improve: support for catalina
- fix: download sources IERS 
- fix: seeing entries visibility upon startup
"""

with open('notes.txt', 'w') as f:
    f.writelines(releaseNotes)

setup(
    name='mountwizzard4',
    version='3.1.0b5',
    packages=[
        'mw4',
        'mw4.base',
        'mw4.gui',
        'mw4.indibase',
        'mw4.gui.extWindows',
        'mw4.gui.extWindows.hemisphere',
        'mw4.gui.extWindows.image',
        'mw4.gui.extWindows.simulator',
        'mw4.gui.mainWmixin',
        'mw4.gui.mainWindow',
        'mw4.gui.utilities',
        'mw4.gui.widgets',
        'mw4.logic.automation',
        'mw4.logic.camera',
        'mw4.logic.cover',
        'mw4.logic.databaseProcessing',
        'mw4.logic.dome',
        'mw4.logic.environment',
        'mw4.logic.file',
        'mw4.logic.filter',
        'mw4.logic.focuser',
        'mw4.logic.measure',
        'mw4.logic.modeldata',
        'mw4.logic.photometry',
        'mw4.logic.plateSolve',
        'mw4.logic.powerswitch',
        'mw4.logic.profiles',
        'mw4.logic.remote',
        'mw4.logic.telescope',
        'mw4.logic.keypad',
        'mw4.mountcontrol',
        'mw4.resource',
    ],
    python_requires='>=3.8.0, <3.11',
    install_requires=[
        'numpy==1.24.2',
        'opencv-python-headless==4.6.0.66',
        'scipy==1.10.1',
        'astropy==5.2.1',
        'pyerfa==2.0.0.1',
        'astroquery==0.4.6',
        'sep==1.2.1',
        'pyqtgraph==0.13.2',
        'qimage2ndarray==1.10.0',
        'skyfield==1.45',
        'sgp4==2.21',
        'requests==2.28.2',
        'requests_toolbelt==0.10.1',
        'importlib_metadata==6.0.0',
        'python-dateutil==2.8.2',
        'deepdiff==6.2.3',
        'wakeonlan==3.0.0',
        'pybase64==1.2.3',
        'websocket-client==1.5.1',
        'hidapi==0.13.1',
        'range-key-dict==1.1.0',
        'ndicts==0.3.0',
        'packaging==23.0',
        'lz4==4.3.2',
        'xisf==0.9.0',
    ]
    + (['pywin32==305'] if platform.system() == "Windows" else [])
    + (['pywinauto==0.6.8'] if platform.system() == "Windows" else [])
    + (['PyQt5==5.15.9'] if platform.machine() not in ['armv7l'] else [])
    + (['PyQt3D==5.15.6'] if platform.machine() not in ['armv7l',
                                                        'aarch64'] else []),
    keywords=['5.15.9'],
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='Michael Wuertenberger',
    author_email='michael@wuertenberger.org',
    description='Tool for managing 10micron mounts',
    long_description=Path("README.rst").read_text(encoding="utf-8"),
    long_description_content_type="text/x-rst",
    project_urls={
        'Documentation': 'https://mworion.github.io/MountWizzard4',
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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
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
