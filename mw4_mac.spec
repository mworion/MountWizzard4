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
#
#  to be done before getting the package right:
#
#  remove try case under astropy.visualisation.wcsaxes.__init__.py for loading pytest
#
# Important: still using virtualenv==16.1.0 because distutils are missing later on

# standard libraries
import os
import sys
import shutil
# external packages
import astropy
# import numpy
# local import
# remove TK

# adding this line helps in virtualenv building packages without problems missing distutils
# see: https://github.com/pyinstaller/pyinstaller/issues/4064
import distutils
if distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)
# end fix


sys.modules['FixTk'] = None

# define paths
astropy_path, = astropy.__path__

block_cipher = None
pythonPath = '/Users/mw/venv/lib/python3.7'
sitePack = pythonPath + '/site-packages'
distDir = './dist'
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
          strip=True,
          upx=False,
          console=False,
          onefile=True,
          icon='mw4.icns',
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

print('Build No:', BUILD_NO)

if os.path.isfile(buildFile):
    os.remove(buildFile)
    print('removed existing app bundle')

app = BUNDLE(exe,
             name='MountWizzard4.app',
             version=4,
             icon='mw4.icns',
             bundle_identifier=None)

