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
# GUI with PySide6 for python3
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
from setuptools import setup, find_packages
from pathlib import Path
import platform

releaseNotes = """
- this is a major release !
  please try out in a separate work folder for test!
  
- add: support for python 3.11, 3.12 and 3.13, remove 3.7, 3.8, 3.9
- add native support for Macs with Apple silicon
- add: support automation with 10micron webservices
- add: support uploading mechanism for databases for macos and linux
- add: show free disk space of work dir in the status bar
- add: support for comet and asteroid data in extended downloads
- add: age parameter for MPC SAT databases before auto download 
- add: new theme with 3d buttons for selection
- change: faster and more reliable uploading mechanism for databases
- change: celestrak interface url's and retrieval strategy
- change: moving PyQt5 to major PySide6
- change: moving libraries to latest
- change: remove old windows automation
- change: remove embedded documentation and replace with online link
- refactor: environment devices (now 3 generic ones)
- refactor: remove installer to separate repo (InstallerMW4)
- refactor: optimizing code for better performance
- refactor: plate solving features more reliable
- refactor: camera handling
- refactor: satellite handling
- refactor: database handling for MPC files
- improve: faster calculation of satellite track using internal calculations
- improve: reduced size of app
- improve: faster startup time
- improve: faster database loading
- improve: optimizing material look & feel fpr simulator 
- improve: don't delete message list when color change
- improve: rewrite of the online documentation
- improve: no 10micron installer needed anymore for object data
- remove: automation of 10micron installer
- fix: typos
"""

with open("notes.txt", "w") as f:
    f.writelines(releaseNotes)

setup(
    name="mountwizzard4",
    version="4.0.0a24",
    packages=find_packages(),
    python_requires=">=3.10.0, <3.14",
    install_requires=[
        "numpy==2.2.6",
        "opencv-python-headless==4.12.0.88",
        "scipy==1.15.3",
        "astropy==6.1.7",
        "pyerfa==2.0.1.5",
        "astroquery==0.4.10",
        "sep==1.4.1",
        "pyqtgraph==0.13.7",
        "qimage2ndarray==1.10.0",
        "skyfield==1.53",
        "sgp4==2.25",
        "requests==2.32.5",
        "requests_toolbelt==1.0.0",
        "importlib_metadata==8.7.0",
        "python-dateutil==2.9.0.post0",
        "wakeonlan==3.1.0",
        "pybase64==1.4.2",
        "websocket-client==1.8.0",
        "hidapi==0.14.0.post4",
        "range-key-dict==1.1.0",
        "ndicts==0.3.0",
        "packaging==25.0",
        "lz4==4.4.4",
        "xisf==0.9.5",
    ]
    + (["pywin32==311"] if platform.system() == "Windows" else []),
    keywords=["6.9.1"],
    url="https://github.com/mworion/MountWizzard4",
    license="APL 2.0",
    author="Michael Wuertenberger",
    author_email="michael@wuertenberger.org",
    description="Tool for managing 10micron mounts",
    long_description=Path("README.rst").read_text(encoding="utf-8"),
    long_description_content_type="text/x-rst",
    project_urls={
        "Documentation": "https://mworion.github.io/MountWizzard4",
        "Source Code": "https://github.com/mworion/mountwizzard4",
        "Bug Tracker": "https://github.com/mworion/mountwizzard4/issues",
        "Discussions": "https://github.com/mworion/MountWizzard4/discussions",
        "Channel": "https://www.youtube.com/user/orion49m/featured",
        "Forum": "https://www.10micron.eu/forum/",
    },
    zip_safe=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Environment :: Other Environment",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Natural Language :: German",
        "Topic :: Documentation :: Sphinx",
    ],
)
