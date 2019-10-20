#!/bin/bash
source venv/bin/activate
cd mountwizzard4
pip install mountcontrol.tar.gz
pip install indibase.tar.gz
pip install mountwizzard4.tar.gz
deactivate
