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
# standard libraries
import os
import sys
import shutil
# external packages
import astropy
# local import
# remove TK
sys.modules['FixTk'] = None

# define paths
DISTPATH = '../dist'
WORKPATH = '../build'
astropy_path, = astropy.__path__

block_cipher = None
pythonPath = '/Users/mw/venv/Lib'
sitePack = pythonPath + '/site-packages'


distDir = '/Users/mw/MountWizzard/dist'
packageDir = '/Users/mw/MountWizzard/mw4'
importDir = '/Users/mw/MountWizzard'

a = Analysis([packageDir + '/loader.py'],
             pathex=[packageDir],
             binaries=[
                 ],
             datas=[
                 (sitePack + '/skyfield/data', './skyfield/data'),
                 (astropy_path, 'astropy'),
             ],
             hiddenimports=[
                 'numpy.lib.recfunctions',
                 'numpy.random.common',
                 'numpy.random.bounded_integers',
                 'numpy.random.entropy',
                 'shelve',
                 ],
             hookspath=[],
             runtime_hooks=[],
             excludes=['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter',
                       'astropy',
                       ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             )

# remove thing to reduce size and number of files in package (have to be extracted)
a.binaries = [x for x in a.binaries if not x[0].startswith('mpl-data/sample_data')]
a.binaries = [x for x in a.binaries if not x[0].startswith('PyQt5/Qt/translations')]
a.binaries = [x for x in a.binaries if not x[0].startswith('QtQuick')]
a.binaries = [x for x in a.binaries if not x[0].startswith('QtQml')]

# same to datas
a.datas = [x for x in a.datas if not x[0].startswith('mpl-data/sample_data')]
a.datas = [x for x in a.datas if not x[0].startswith('PyQt5/Qt/translations')]
a.datas = [x for x in a.datas if not x[0].startswith('QtQuick')]
a.datas = [x for x in a.datas if not x[0].startswith('QtQml')]

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher,
          )

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='MountWizzard4',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='mw4.ico',
          )

#
# we have to prepare the build as there is an error when overwriting it
# if file present, we have to delete python3 --version
#

sys.path.append(importDir)
from mw4.mainApp import MountWizzard4
BUILD_NO = MountWizzard4.version

print(BUILD_NO)

app = BUNDLE(exe,
             name='MountWizzard4.exe',
             version=4,
             icon='mw4.ico',
             bundle_identifier=None)
