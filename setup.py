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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
from setuptools import setup
from pathlib import Path
import platform

releaseNotes = """
- this is a major release !
- add: support for python 3.11 and 3.12, remove 3.7 and 3.8
- add: support automation with 10micron webservices
- add: support uploading mechanism for databases for macos and linux
- change: faster and more reliable uploading mechanism for databases
- change: moving PyQt5 to major version PyQt6
- change: moving libraries to latest versions
- change: remove old windows automation
- change: remove embedded documentation and replace with online link
- refactoring: environment devices (now 3 generic ones)
- refactoring: remove installer to separate repo (InstallerMW4)
- fix: typos
"""

with open('notes.txt', 'w') as f:
    f.writelines(releaseNotes)

setup(
    name='mountwizzard4',
    version='4.0.0a2',
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
    python_requires='>=3.9.0, <3.13',
    install_requires=[
        'numpy==1.26.4',
        'opencv-python-headless==4.9.0.80',
        'scipy==1.13.0',
        'astropy==6.1.0',
        'pyerfa==2.0.1.4',
        'astroquery==0.4.7',
        'sep_mw4==1.2.2',
        'pyqtgraph==0.13.7',
        'qimage2ndarray==1.10.0',
        'skyfield==1.48',
        'sgp4==2.23',
        'requests==2.31.0',
        'requests_toolbelt==1.0.0',
        'importlib_metadata==7.1.0',
        'python-dateutil==2.9.0.post0',
        'wakeonlan==3.1.0',
        'pybase64==1.3.2',
        'websocket-client==1.8.0',
        'hidapi==0.14.0',
        'range-key-dict==1.1.0',
        'ndicts==0.3.0',
        'packaging==24.0',
        'lz4==4.3.3',
        'xisf==0.9.5',
    ]
    + (['pywin32==306'] if platform.system() == "Windows" else [])
    + (['PyQt6==6.7.0'] if platform.machine() not in ['armv7l'] else [])
    + (['PyQt6-3D==6.7.0'] if platform.machine() not in ['armv7l', 'aarch64'] else[]),
    keywords=['6.7.0'],
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
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 11',
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
