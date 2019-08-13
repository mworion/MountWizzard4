#!/bin/bash
source venv/bin/activate
cd test
pip install mc.tar.gz
pip install ib.tar.gz
pip install mw4.tar.gz
deactivate
