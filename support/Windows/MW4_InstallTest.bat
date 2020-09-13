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

echo Checking environment and start script > install.log

rem get version of python installation
for /f "delims=" %%a in ('python --version') do @set T=%%a

echo variable T has value of %T% >> install.log

echo %T% | find "3.8" > nul
if not errorlevel 1 SET P_VER='python3.8'

echo %T% | find "3.7" > nul
if not errorlevel 1 SET P_VER='python3.7'

echo %T% | find "3.6" > nul
if not errorlevel 1 SET P_VER='python3.6'

echo variable P_VER has value of %P_VER% >> install.log

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

echo . >> install.log
echo Checking 32/64 bit OS >> install.log
echo variable OS has value of %OS% >> install.log
echo %OS% | find "32" > nul
if errorlevel 1 goto :64bit

echo python 32bit installed >> install.log
echo.
echo ---------------------------------------------
echo python 32Bit installed
echo ---------------------------------------------
echo.
goto :proceedVirtualenv

:64bit

echo python 64bit installed >> install.log
echo.
echo ---------------------------------------------
echo python 64Bit installed
echo ---------------------------------------------
echo.

:proceedVirtualenv
echo . >> install.log
echo installing wheel >> install.log
python -m pip install wheel --disable-pip-version-check >> install.log

:proceedSetupVirtualenv
rem installing virtual environment
echo.
echo ---------------------------------------------
echo Installing %P_VER% in virtual environ
echo ---------------------------------------------
echo.

echo . >> install.log
echo Installing %P_VER% in virtual environ >> install.log
python -m venv venv >> install.log
if not errorlevel 1 goto :proceedInstallMW4

echo.
echo ---------------------------------------------
echo No valid virtual environment installed
echo Please check the install.log for errors
echo ---------------------------------------------
echo.

exit

:proceedInstallMW4

echo.
echo ---------------------------------------------
echo Installing mountwizzard4 - take a minute
echo ---------------------------------------------
echo.

echo . >> install.log
echo Installing mountwizzard4 - take a minute >> install.log
venv\Scripts\activate && python -m pip install mountwizzard4.tar.gz --disable-pip-version-check >>install.log

echo.
echo ---------------------------------------------
echo Installed mountwizzard4 successfully
echo For details see install.log
echo ---------------------------------------------
echo.

echo .
echo MountWizzard4 successfully installed >> install.log