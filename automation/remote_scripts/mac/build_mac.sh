#!/bin/bash
PATH=/Library/Frameworks/Python.framework/Versions/3.7/bin:$PATH
source venv/bin/activate
cd MountWizzard
pip install mountcontrol.tar.gz
pip install indibase.tar.gz
tar -xvzf mountwizzard4.tar.gz --strip-components=1
# pip install pyinstaller==3.5
# pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip
pyinstaller -y mw4_mac.spec
deactivate
#chmod 777 set_image.py
#./set_image.py laufwerk_mw4.png dist/MountWizzard4.dmg
