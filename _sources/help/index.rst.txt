Troubleshooting Q&A and hints
=============================
Based on many feedbacks and solved issues, please check first if your question
already has some answers or at least some hints how to improve the situation.

Installation
------------
Despite MW4 will run on many platforms, your setup might have some special
constrains which need to taken into account. In the following I try to refer to
the important ones.

Python
^^^^^^
MW4 runs on python 3.7 - 3.9. On other versions scripts will will fail and MW4
will not run.

Windows version needs at least 3.8.2 to allow automation.

Windows 7 might be using, but is not tested. Other windows versions are not
supported.

On windows, you need to select if you are using 32bit or 64bit python depending
on drivers you are using for your devices. 32bit and 64bit could not be mixed !

Normally you will use a preinstalled python version (if that fits) or use a python
version from python.org. Please do not use other sources.

As MW4 lives in a virtual environment, updating python does not automatically
update the virtual environment. If you need to update python for any reason there
are two possibilities: New install of MW4 in a new work dir or deleting the
venv folder in your actual work dir and running the install script again.

MW4 App
^^^^^^^
There is no need for running MW4 with admin rights. If so, something is wrong.

MW4 will run in a virtual environment. Please do not try to install MW4 as a
system application as this might interfere with other installations.

MW4 does not behave as expected: please post a log and describe the procedure in
steps. If you could add screen shots this helps a lot.

MW4 Updating does fail
^^^^^^^^^^^^^^^^^^^^^^
Since v2 MW4 should be able to handle all updates / downgrades with the internal
updater. From v1 to v2 windows needs the MW4_Update.bat script as the internal
updater can't free used windows libraries. MacOSx and Linux should be fine.

Scripts
^^^^^^^
Installation does not need admin rights. If so, please check the folder locations.
In windows10 desktop and some other folder are not writable for applications.

The scripts do nothing special, you could use for many topics manual commands as
well. Unfortunately the scripts could not manage all special setups, but feel free
to change them accordingly.

On RaspberryPi4 (arm64), the scripts try to use precompiled wheels from github.
This increases speed. But in some circumstances, compile on your system might be
necessary. If so, you need to have a compiler and environments installed as well.

On RaspberryPi3 you need to compile the environment partly yourself. An
installation only with scripts will not work.

Mount connectivity
------------------
MW4 only supports IP links. As data latency is a critical topic, please use a
wired connection to the mount. Wireless connection might have some drops in
connections (you will see this with mount button switching red / green multiple
times)

Please check your IP settings, gateways if first connections fail.

If your WOL does not work, please check MAC address, WOL being enabled. If you
switched your mount manual off and cut the power supply, sometimes WOL does not
work the first time. You need a redundant path if you are in a remote site!

Basically multiple instances of MW4 could be up and running, but MW4 take up to 6
parallel connections to the mount. The documentation allows in total 10 connection
each of the two ports (3490, 3492). This might overload the 10 micron system.

Device connectivity
-------------------

ASCOM Device does not work / connect
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ASCOM uses different types of drivers for the devices. Some of them need an
environment in 32bit or 64bit like you application. So if you are using an 64bit
application for imaging your drivers will be 64bit compatible. In this case the
python installation also needs to be 64bit. Otherwise the connection will fail.

Modern CMOS cameras with large sensors normally work on 64bit mode.

Many device driver only support one connection at the same time. So if you imaging
application already *took* a device, MW4 might be not able to connect anymore.

Please test your setup running with ASCOM suite (included in ASCOM platform
installation) or any other programs you good know to test device functions outside
MW4.

Model building
--------------

Updating IERS/SAT/MPC data
--------------------------

Data could not be uploaded
^^^^^^^^^^^^^^^^^^^^^^^^^^
All data uploads within MW4 use the 10micron updater. The updater is only
available on windows and has to be installed.

MW4 does a windows automation. So it steers the original application and automates
all user interactions. This might take time. Please wait until MW4 has finished
it's job. Please do not interact on your PC during this time with mouse or
keyboard as they disturb the automation process.

In any case MW4 has downloaded or prepared the data for upload. This is also valid
for non windows platforms.

Data could not be fetched from internet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You need an internet connection and set MW4 in online mode to download new data
for upload.

Tracking satellites
-------------------

Logfiles and reports
--------------------

Where could I change the log level ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The log level could be changed under settings misc. The default setting is warning.
If you need analyzes, please go to debug. If a driver or mount connectivity is
related as well, please go to trace. Please be aware that log file especially in
trace mode could become big.

.. image:: image/log_level.png
    :align: center
    :scale: 71%

