#!/bin/bash
source mw4/bin/activate
cd mountwizzard4
pip install mountcontrol-*.tar.gz
pip install indibase-*.tar.gz
pip install mw4-*.tar.gz
chmod 777 start.sh
DISPLAY=:0.0 ./start.sh
