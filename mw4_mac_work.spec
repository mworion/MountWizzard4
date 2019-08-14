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

# standard libraries
import os
import sys
import shutil
# external packages
import astropy
# import numpy
# local import


# adding this line helps in virtualenv building packages without problems missing distutils
# see: https://github.com/pyinstaller/pyinstaller/issues/4064
import distutils
if distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)
# end fix

# remove TK
sys.modules['FixTk'] = None

# define paths
astropy_path, = astropy.__path__

block_cipher = None
pythonPath = '/Users/q115346/PycharmProjects/Envs/mw4/lib/python3.7'
sitePack = pythonPath + '/site-packages'
distDir = './dist'
packageDir = '/Users/q115346/PycharmProjects/MountWizzard4/mw4'
importDir = '/Users/q115346/PycharmProjects/MountWizzard4'

a = Analysis(['mw4/ui_basics.py'],
             pathex=[packageDir],
             binaries=[
                 ],
             datas=[
                    (sitePack + '/skyfield/data', './skyfield/data'),
                    (astropy_path, 'astropy'),
             ],
             hiddenimports=['shelve',
                            'numpy.lib.recfunctions',
                            'numpy.random.common',
                            'numpy.random.bounded_integers',
                            'numpy.random.entropy',
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

# same to datas
a.datas = [x for x in a.datas if not x[0].startswith('mpl-data/sample_data')]

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
          console=True,
          onefile=True,
          icon='automation/images/mw4.icns',
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
             icon='automation/images/mw4.icns',
             bundle_identifier=None)

