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

.. code-block:: bash
    uv --version

If you get the version number, everything is perfect.

Installing python and the virtual environment
---------------------------------------------
There is no need to have python installed on the forehand and there no dependency
to any python installation already present with the use of uv. Mountwizzard4 v3
plays on python 3.8 - 3.10, so I would recommend to use the n ewest one 3.10. For
installing, please choose a work folder for Mountwizzard4, open a terminal window
and change directory to this work folder. the command

.. code-block:: bash

    uv venv -p 3.10

does download the right python package (3.10) and installs a virtual environment
in you work folder. The virtual environment is stored in a directory there called
".venv".

Installing MountWizzard4
------------------------
The installation is now a simple command:

.. code-block:: bash

    uv pip install mountwizzard4

Installation will download the necessary packages (visible) and installs them in
the virtual environment.

If you want to have a dedicated version of MountWizzard4, just add the version
number in the command line (e.g. 3.2.8) like

.. code-block:: bash

    uv pip install mountwizzard4==3.2.8

Changing versions upgrade and downgrade work the same way just with the appropriate
version numbers.

Run MountWizzard4
-----------------
Once everything installed running MountWizzard4 is also a simple command:

.. code-block:: bash

    uv run mw4

If you would like some options please use the command line parameters
MountWizzard4 supports. These are setting for the appearance sizes on windows
primary:

Basically that's it.

Command line options
--------------------
MountWizzard4 supports a number of command line options:

.. code-block:: bash

    '-d', '--dpi'

Setting QT font DPI (+dpi = -fontsize, default=96)

.. code-block:: bash

    '-s', '--scale'

Setting Qt DPI scale factor (+scale = +size, default=1)

.. code-block:: bash

    '-h', '--help'

Getting this information.

Additional for RaspberryPi (4, 5)
---------------------------------

.. hint::
    This is only necessary for v3. MountWizzard4 v4 brings all binaries directly.
    For v4 just proceed like above.

If you want to install MountWizzard4 v3 to an Raspi or ARM64 based computer,
please follow the installation process. of uv, python and virtual environment.
Before starting MountWizzard4 v3 you need to install some precompiled packages
as they were not available for the necessary python 3.8-3.10 versions. For that
use the same terminal window pointing to you work folder and add the two following
commands:

.. code-block:: bash

    uv pip install https://github.com/mworion/mountwizzard4/raw/main/wheels/PyQt5-5.15.9-cp38.cp39.cp310-abi3-manylinux_2_17_aarch64.whl

After that, please proceed with the use of MountWizzard4 like described
above.