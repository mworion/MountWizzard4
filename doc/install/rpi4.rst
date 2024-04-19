Install on RaspberryPi 4
========================

.. hint:: The simplest raspi installation for rpi3 works with astroberry

We are installing MW4 on an ubuntu 20.04.1LTS 64Bit system. In relation to the
RPi3 it seems to be much simpler to do. Nevertheless some of the big packages will
be compiled on your system during installation, which means this will take some
time (hours). There is the opportunity to use precompiled packages out of the
install scripts provided.

Another big step forward is that you could use now a virtual environment for
installing MW4.

Installing Python on RPi4
-------------------------

To get MW4 installed on RPi4 you will follow the instructions of Dustin Casto:

https://homenetworkguy.com/how-to/install-ubuntu-mate-20-04-lts-on-raspberry-pi-4/

to get Ubuntu Mate 20.04.1 LTS on your RPi4.

.. hint::
    Some users experience problems with KStars/EKOS on original ubuntu-mate
    desktop. So the recommendation is to use a KDE bases desktop like kubuntu. The
    easiest way to install a desktop on top of the server installation is using:
    https://github.com/wimpysworld/desktopify

After you have finished the setup and got the desktop up and running, the command

.. code-block:: python

    python3 --version

should give you the following result 3.8.5: Please take care, that a python
version 3.8.5 or later is installed.

The actual Ubuntu mate 20.04.1LTS distribution comes with python 3.8.5, so
everything should be OK. Next we have to do is to install a virtual environment
capability, the packet manager pip and the development headers for python to be
able to compile necessary packages:

.. code-block:: python

    sudo apt-get install python3.8-venv
    sudo apt-get install python3-pip
    sudo apt-get install qt5-default

.. note::
    You need to have both packages installed as otherwise the install script or
    later does MW4 not run.


Using the precompiled wheels
----------------------------
Please choose the script fitting to you ubuntu version (18.04.x or 20.04.x)
The scripts will use precompiled wheels for aarch64 as much as possible to improved
the installation speed e.g. on your RPi4.

.. code-block:: python

    ./MW4_Install_aarch64_18_04.sh

    or

    ./MW4_Install_aarch64_20_04.sh

After a short while MW4 is installed and should be ready to run like in ubuntu
installation.

.. note:: The install scripts only support python 3.8-3.9 versions"

