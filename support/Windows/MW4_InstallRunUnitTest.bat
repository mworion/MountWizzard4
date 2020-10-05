@echo off
rem
rem Installer for Win10
rem (c) 2020 mworion
rem

rem starting a new install log
echo.
echo ---------------------------------------------
echo Checking installed python version
echo ---------------------------------------------
echo.

echo Checking environment and start script

rem get version of python installation
for /f "delims=" %%a in ('python --version') do @set T=%%a

echo variable T has value of %T%

echo %T% | find "3.8" > nul
if not errorlevel 1 SET P_VER='python3.8'

echo %T% | find "3.7" > nul
if not errorlevel 1 SET P_VER='python3.7'

echo %T% | find "3.6" > nul
if not errorlevel 1 SET P_VER='python3.6'

echo variable P_VER has value of %P_VER%

echo %P_VER% | find "python" > nul
if not errorlevel 1 goto :proceed32Bit

echo.
echo ---------------------------------------------
echo No valid python version installed
echo ---------------------------------------------
echo.

exit

:proceed32Bit
rem write python test file
echo import platform > test.py
echo print(platform.architecture()[0]) >> test.py

for /f "delims=" %%a in ('python test.py') do @set OS=%%a
rem delete python test file
del test.py

echo .
echo Checking 32/64 bit OS
echo variable OS has value of %OS%
echo %OS% | find "32" > nul
if errorlevel 1 goto :64bit

echo python 32bit installed
echo.
echo ---------------------------------------------
echo python 32Bit installed
echo ---------------------------------------------
echo.
goto :proceedVirtualenv

:64bit

echo python 64bit installed
echo.
echo ---------------------------------------------
echo python 64Bit installed
echo ---------------------------------------------
echo.

:proceedVirtualenv
echo .
echo installing wheel
python -m pip install wheel --disable-pip-version-check

rem installing virtual environment
echo.
echo ---------------------------------------------
echo Installing %P_VER% in virtual environ
echo ---------------------------------------------
echo.

echo .
echo Installing %P_VER% in virtual environ
python -m venv venv
if not errorlevel 1 goto :proceedUnitTest

echo.
echo ---------------------------------------------
echo No valid virtual environment installed
echo Please check the install.log for errors
echo ---------------------------------------------
echo.

exit

:proceedUnitTest

echo.
echo ---------------------------------------------
echo Installing Unittests pytest
echo ---------------------------------------------
echo.
venv\\Scripts\\activate && python -m pip install pytest --disable-pip-version-check
venv\\Scripts\\activate && python -m pip install pytest-qt --disable-pip-version-check
venv\\Scripts\\activate && python -m pip install pytest-cov --disable-pip-version-check
venv\\Scripts\\activate && python -m pip install pytest-pythonpath --disable-pip-version-check


echo.
echo ---------------------------------------------
echo Cloning GitHub
echo ---------------------------------------------
echo.
git clone https://github.com/mworion/MountWizzard4.git
