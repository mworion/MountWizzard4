#!/bin/bash
PATH=/Library/Frameworks/Python.framework/Versions/3.7/bin:$PATH
cd /Users/mw/mountwizzard4
source /Users/mw/venv/bin/activate
/Users/mw/venv/bin/python /Users/mw/venv/lib/python3.7/site-packages/mountwizzard4/loader.py
test
deactivate