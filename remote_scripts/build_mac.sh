#!/bin/bash
PATH=/Library/Frameworks/Python.framework/Versions/3.7/bin:$PATH
source venv/bin/activate
cd MountWizzard
#pip install mc.tar.gz
#pip install ib.tar.gz
#pip install pyinstaller==3.5
#pip install dmgbuild
#tar -xvzf mw4.tar.gz --strip-components=1
# pyinstaller -y mw4_mac.spec
# rm -rf ./dist/*.dmg
# dmgbuild -s dmg_settings.py "MW4" MW4.dmg
deactivate
chmod 777 set_image.py
./set_image.py mw4.png dist/MountWizzard4.dmg
