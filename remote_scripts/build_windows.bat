venv\Scripts\activate.bat
cd MountWizzard
pip install mc.tar.gz
pip install ib.tar.gz
pip install pyinstaller==3.5
tar -xvzf mw4.tar.gz --strip-components=1
pyinstaller -y mw4_windows.spec
deactivate

