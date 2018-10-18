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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
#
#
#
import os
import shutil
DISTPATH = '../dist'
WORKPATH = '../build'

BUILD_NO = '0.1.dev0'

block_cipher = None
pythonPath = '/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6'
distDir = '/Users/mw/PycharmProjects/MountWizzard4/dist'


a = Analysis(['mountwizzard4/mw4_loader.py'],
    pathex=['/Users/mw/PycharmProjects/MountWizzard4/mountwizzard4'],
    binaries=[
        ],
    datas=[
        ],
    hiddenimports=[
        ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    )

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
          console=True,
          # onefile=True,
          onefile=True,
          icon='./mountwizzard4/media/mw4.icns',
          # exclude_binaries=True,
          )

#
# we have to prepare the build as there is an error when overwriting it
# if file present, we have to delete it
#

buildFile = distDir + '/MountWizzard4.app'
buildFileNumber = distDir + '/mountwizzard4-' + BUILD_NO + '.app'

print(BUILD_NO)

if os.path.isfile(buildFile):
    os.remove(buildFile)
    print('removed existing app bundle')

app = BUNDLE(exe,
             name='MountWizzard4.app',
             version=4,
             icon='./mountwizzard4/media/mw4.icns',
             bundle_identifier=None)

#
# we have to prepare the build as there is an error when overwriting it
# if file present, we have to delete it
#

if os.path.isdir(buildFileNumber):
    shutil.rmtree(buildFileNumber)
    print('removed existing app bundle with version number')

os.rename(buildFile, buildFileNumber)