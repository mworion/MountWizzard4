if exist venv (rmdir /s/q venv)
python -m venv venv
venv\Scripts\activate
pip install PyQt5==5.13
pip install astropy==3.1.2
pip install matplotlib==3.1.1
pip install wakeonlan==1.1.6
pip install requests==2.22.0
pip install requests-toolbelt==0.9.1
pip install skyfield==1.10
pip install qimage2ndarray
deactivate