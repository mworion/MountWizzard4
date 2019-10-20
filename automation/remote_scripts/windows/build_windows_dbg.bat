venv\Scripts\activate.bat
cd MountWizzard
pip install mountcontrol.tar.gz
pip install indibase.tar.gz
pip install https://github.com/pyinstaller/pyinstaller/tarball/develop
tar -xvzf mountwizzard4.tar.gz --strip-components=1
pyinstaller -y mw4_windows_dbg.spec
deactivate