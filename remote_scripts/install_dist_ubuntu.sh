#!/bin/bash
source venv/bin/activate
cd mountwizzard4
pip install mc.tar.gz
pip install ib.tar.gz
pip install mw4.tar.gz
chmod 777 start.sh
DISPLAY=:0.0 start_ubuntu.sh
