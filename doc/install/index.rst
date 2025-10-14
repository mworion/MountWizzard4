Installation
============
MountWizzard4 v4 (and also valid for v3) will change the way of installation. As
it relies on python and uses a virtual environment the whole process got to
complicated to maintain and was not easy for the users to follow. Therefore
installation changes to an overall public free solution called **uv**.

**uv** is able to handle python installations and versioning,
activating and deactivating of virtual environments, installing and
versioning MountWizzard4 an that all with only 3 commands across all supported
platforms (Windows, Linux and MacOS).

Installing **uv**
-----------------
I strongly recommend to install uv as a standalone program. The description could
be found here: https://docs.astral.sh/uv/getting-started/installation/. To install
do the following steps:

- open a terminal window on your system
- select from the install page your corresponding OS
- copy and paste the install script and let it run

After that, uv is installed. To move on, your terminal is not aware of the new
features of uv. The simplest way to do get to this point is to close the terminal
windows and open a new one.

Please check the presence of uv with the command

uv --version

If you get the version number, everything is perfect.

Installing python and the virtual environment
---------------------------------------------
There is no need to have python installed on the forehand and there no dependency
to any python installation already present with the use of uv. Mountwizzard4 v3
plays on python 3.8 - 3.10, so I would recommend to use the n ewest one 3.10. For
installing, please choose a work folder for Mountwizzard4, open a terminal window
and change directory to this work folder. the command

uv venv -p 3.10

does download the right python package (3.10) and installs a virtual environment
in you work folder. The virtual environment is stored in a directory there called
".venv".

Installing MountWizzard4
------------------------
The installation is now a simple command:

uv pip install mountwizzard4

Installation will download the necessary packages (visible) and installs them in
the virtual environment.

If you want to have a dedicated version of MountWizzard4, just add the version
number in the command line (e.g. 3.2.8) like

uv pip install mountwizzard4==3.2.8

Changing versions upgrade and downgrade work the same way just with the appropriate
version numbers.

Run MountWizzard4
-----------------
Once everything installed running MountWizzard4 is also a simple command:

uv run mw4

If you would like some options please use the command line parameters
MountWizzard4 supports. These are setting for the appearance sizes on windows
primary:

Basically that's it.

