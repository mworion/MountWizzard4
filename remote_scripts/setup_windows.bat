if exist mw4 (rmdir /s/q mw4)
if exist mountwizzard4 (rmdir /s/q mountwizzard4)
mkdir mountwizzard4
python -m venv mw4
mw4\Scripts\activate.bat
pip install PyQt5==5.12.2
pip install astropy==3.1.2
pip install matplotlib==3.1.1
pip install wakeonlan==1.1.6
pip install requests==2.22.0
pip install requests-toolbelt==0.9.1
pip install skyfield==1.10
deactivate