#!/bin/bash
PATH=/Library/Frameworks/Python.framework/Versions/3.7/bin:$PATH
source venv/bin/activate
cd MountWizzard
pip install mc.tar.gz
pip install ib.tar.gz
pip install pyinstaller==3.5
tar -xvzf mw4.tar.gz --strip-components=1
pyinstaller -y mw4_mac.spec
hdiutil create ./dist/MountWizzard4.dmg -srcfolder ./dist/*.app -ov
deactivate