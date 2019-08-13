#!/bin/bash
PATH=/Library/Frameworks/Python.framework/Versions/3.7/bin:$PATH
source venv/bin/activate
cd MountWizzard
pip install dmgbuild
dmgbuild -s dmg_settings.py "MW4" MW4.dmg
deactivate