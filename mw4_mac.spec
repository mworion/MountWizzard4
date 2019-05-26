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
# import numpy
# local import
# remove TK
sys.modules['FixTk'] = None

# define paths
DISTPATH = '../dist'
WORKPATH = '../build'
astropy_path, = astropy.__path__

block_cipher = None
pythonPath = '/Users/mw/PycharmProjects/Envs/mw4/lib/Python3.7'
sitePack = pythonPath + '/site-packages'
distDir = '/Users/mw/PycharmProjects/MountWizzard4/dist'
packageDir = '/Users/mw/PycharmProjects/MountWizzard4/mw4'
importDir = '/Users/mw/PycharmProjects/MountWizzard4'

a = Analysis(['mw4/loader.py'],
             pathex=[packageDir],
             binaries=[
                 ],
             datas=[
                    (sitePack + '/skyfield/data', './skyfield/data'),
                    (astropy_path, 'astropy'),
             ],
             hiddenimports=['shelve',
                            'numpy.lib.recfunctions',
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
a.binaries = [x for x in a.binaries if not x[0].startswith('mpl-data/fonts')]
a.binaries = [x for x in a.binaries if not x[0].startswith('PyQt5/Qt/translations')]
a.binaries = [x for x in a.binaries if not x[0].startswith('QtQuick')]
a.binaries = [x for x in a.binaries if not x[0].startswith('QtQml')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/analytic_functions')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/config.tests')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/constants.tests')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/convolution')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/cosmology')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/samp')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/modeling')]
## a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/table')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/vo')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/wcs/tests')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/visualization/tests')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('astropy/utils/tests')]

# same to datas
a.datas = [x for x in a.datas if not x[0].startswith('mpl-data/sample_data')]
a.datas = [x for x in a.datas if not x[0].startswith('mpl-data/fonts')]
a.datas = [x for x in a.datas if not x[0].startswith('PyQt5/Qt/translations')]
a.datas = [x for x in a.datas if not x[0].startswith('QtQuick')]
a.datas = [x for x in a.datas if not x[0].startswith('QtQml')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/analytic_functions')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/config.tests')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/constants.tests')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/convolution')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/cosmology')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/samp')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/modeling')]
## a.datas = [x for x in a.datas if not x[0].startswith('astropy/table')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/vo')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/wcs/tests')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/visualization/tests')]
# a.datas = [x for x in a.datas if not x[0].startswith('astropy/utils/tests')]

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher,
          )

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='mountwizzard4',
          debug=True,
          strip=True,
          upx=False,
          console=False,
          onefile=True,
          icon='./mw4/gui/media/mw4.icns',
          # exclude_binaries=True,
          )

#
# we have to prepare the build as there is an error when overwriting it
# if file present, we have to delete python3 --version
#

sys.path.append(importDir)
from mw4.mainApp import MountWizzard4
BUILD_NO = MountWizzard4.version

buildFile = distDir + '/MountWizzard4.app'
buildFileNumber = distDir + '/mountwizzard4-' + BUILD_NO + '.app'

print(BUILD_NO)

if os.path.isfile(buildFile):
    os.remove(buildFile)
    print('removed existing app bundle')

app = BUNDLE(exe,
             name='MountWizzard4.app',
             version=4,
             icon='./mw4/gui/media/mw4.icns',
             bundle_identifier=None)

#
# we have to prepare the build as there is an error when overwriting it
# if file present, we have to delete it
#

if os.path.isdir(buildFileNumber):
    shutil.rmtree(buildFileNumber)
    print('removed existing app bundle with version number')

os.rename(buildFile, buildFileNumber)
