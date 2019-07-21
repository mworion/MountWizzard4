if exist mountwizzard4 (rmdir /s/q mountwizzard4)
mkdir mountwizzard4
mw4\Scripts\activate.bat
cd mountwizzard4
pip install mc.tar.gz
pip install ib.tar.gz
pip install mw4.tar.gz
start_windows.bat
deactivate

