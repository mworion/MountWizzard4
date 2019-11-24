#!/bin/zsh
cd $(dirname "$0")
source ./venv/bin/activate
pip install mountwizzard4 --upgrade --no-cache-dir
deactivate
