#!/bin/bash
PATH=/Library/Frameworks/Python.framework/Versions/3.7/bin:$PATH
source venv/bin/activate
cd MountWizzard
pip install mc.tar.gz
pip install ib.tar.gz
tar -xvzf mw4.tar.gz --strip-components=1
pip install pyinstaller==3.5
pyinstaller -y mw4_mac.spec
deactivate
#chmod 777 set_image.py
#./set_image.py laufwerk_mw4.png dist/MountWizzard4.dmg
