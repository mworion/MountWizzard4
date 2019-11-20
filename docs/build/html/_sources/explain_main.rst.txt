Explaining MW4
==============

Layout of main window
---------------------

After starting MW4 the first time you will see the main window. It consists of 4 areas to be
used:

.. image:: _static/explain_main_1.png
    :align: center

Area 1

...describes the actual status of the important devices for modeling, shows status text
outputs from devices and open / shows status / closes additional windows for further work.

Area 2

...shows actual computer time, UTC, and the actual profile. In header section there is
hint if MW4 work actually in online (internet connected) or offline mode.

Area 3

...manages loading / saving profiles, boot and shutdown of the mount (if WOL is enabled
and the MAC address of the mount is known)

Area 4

...shows different tabs for different use cases.

MW4 comes with tooltips which should help you to understand which button or widget is used
for what.

MW4 uses a direct IP connection to the mount computer. This could be done via ethernet cable
or wireless. A RS-232 connection is not supported ! The IP connection is heavily used to
make things happening and updating quick, so there is real traffic on this line.

.. note::
    Recommendation: If possible use MW4 with a wired IP connection (ethernet cable). This
    enables the WOL (wake on lan) function and has lower latency for the IP traffic. Using a
    bad WiFi connection might cause timeouts in communication.

When connected MW4 uses for all functions (except the computer time shown in area 2) the
timebase of the mount. This is also valid for the UTC shown in area 2 as well for other
functions or data using time. You could choose yourself, how the time base of the mount is
tracked by using a NTP solution, the 10micron tool or using GPS during boot also for time
update.

Mount tab
---------

As soon as the mount is connected, the mount tab shows the telescope pointing in hour angle
(HA), right ascension (RA), declination (DEC) in hours / degrees HMS/DMS as well in decimals
. You could choose if you want to see the coordinates in JNow, the mount representation or
in J2000 Epoch for better compatibility to other programs. The handling of coordinates
between MW4 and the mount computer is done in JNow. But this is folly transparent for the
usage.

.. image:: _static/explain_mount_tab.png
    :align: center

In addition altitude (ALT) and azimuth (AZ) is shown in degrees.

In the tracking / flip section the tracking could be switch on / off and if possible a flip
could be forced. The main tracking speed (lunar, solar or sidereal) is highlighted and could
be changed.

Parking / emergency stop put the mount in park position or stops and movement immediately.

In Status and settings from mount computer many parameters are visible and could be altered.
Whenever you see a frame around a value, you could click on it and change the parameter.
Some of the parameters could only be changed if the mount is connected.