#!/bin/zsh
cd $(dirname "$0")
pip3 install virtualenv
virtualenv venv -p python3.7
source ./venv/bin/activate
pip install mountwizzard4 --upgrade --no-cache-dir
deactivate
