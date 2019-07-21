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
pythonPath = '/Users/astro/Envs/mw4/Lib'
sitePack = pythonPath + '/site-packages'


distDir = '/Users/astro/PycharmProjects/MountWizzard4/dist'
packageDir = '/Users/astro/PycharmProjects/MountWizzard4/mw4'
importDir = '/Users/astro/PycharmProjects/MountWizzard4'

a = Analysis([packageDir + '/loader.py'],
             pathex=[packageDir],
             binaries=[
                 ],
             datas=[
                 (sitePack + '/skyfield/data', './skyfield/data'),
                 (astropy_path, 'astropy'),
                 # (sitePack + '/mountcontrol', './mountcontrol'),
                 # (sitePack + '/indibase', './indibase'),
             ],
             hiddenimports=[
                 'numpy.lib.recfunctions',
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
          debug=True,
          strip=False,
          upx=False,
          console=True,
          icon='./mw4/gui/media/mw4.ico',
          )

#
# we have to prepare the build as there is an error when overwriting it
# if file present, we have to delete python3 --version
#

sys.path.append(importDir)
from mw4.mainApp import MountWizzard4
BUILD_NO = MountWizzard4.version

buildFile = distDir + '/MountWizzard4.exe'
buildFileNumber = distDir + '/mountwizzard' + BUILD_NO + '-console.exe'

print(BUILD_NO)

app = BUNDLE(exe,
             name='MountWizzard4.exe',
             version=4,
             icon='./mw4/gui/media/mw4.ico',
             bundle_identifier=None)

#
# we have to prepare the build as there is an error when overwriting it
# if file present, we have to delete it
#

if os.path.isdir(buildFileNumber):
    shutil.rmtree(buildFileNumber)
    print('removed existing app bundle with version number')

os.rename(buildFile, buildFileNumber)