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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
from setuptools import setup
from pathlib import Path
import platform

setup(
    name='mountwizzard4',
    version='0.152.0a1',
    packages=[
        'mw4',
        'mw4.base',
        'mw4.gui',
        'mw4.gui.extWindows',
        'mw4.gui.extWindows.simulator',
        'mw4.gui.mainWmixin',
        'mw4.gui.mainWindow',
        'mw4.gui.utilities',
        'mw4.gui.widgets',
        'mw4.logic.astrometry',
        'mw4.logic.cover',
        'mw4.logic.dome',
        'mw4.logic.environment',
        'mw4.logic.imaging',
        'mw4.logic.measure',
        'mw4.logic.modeldata',
        'mw4.logic.powerswitch',
        'mw4.logic.remote',
        'mw4.logic.telescope',
        'mw4.resource',
    ],
    python_requires='>=3.6.0, <3.9',
    install_requires=[
        'mountcontrol==0.174.0',
        'indibase==0.138',
        'numpy==1.19.0',
        'PyQt5==5.14.2; platform_machine != "armv7l"',
        'PyQt3D==5.14.0; platform_machine != "armv7l"',
        'PyQtWebEngine==5.14.0; platform_machine != "armv7l"',
        'matplotlib==3.3.1',
        'astropy==4.0.1',
        'photutils==0.7.2',
        'scipy==1.5.1',
        'requests==2.23.0',
        'requests_toolbelt==0.9.1',
        'skyfield==1.26',
        'qimage2ndarray==1.8.3',
        'importlib_metadata==1.7.0',
        'opencv-python-headless==4.3.0.36',
    ]
    + (['pywin32==228'] if "Windows" == platform.system() else []),
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='mworion',
    author_email='michael@wuertenberger.org',
    description='tool for a 10micron mount',
    long_description=Path("README.rst").read_text(encoding="utf-8"),
    long_description_content_type="text/x-rst",
    project_urls={
        'Documentation': 'https://mountwizzard4.readthedocs.io',
        'Source Code': 'https://github.com/mworion/mountwizzard4',
        'Bug Tracker': 'https://github.com/mworion/mountwizzard4/issues',
        'Forum': 'https://www.10micron.eu/forum/',
    },
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Environment :: Other Environment',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: MacOS :: MacOS X',
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
