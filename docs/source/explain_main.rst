Explaining MW4
==============

Layout of main window
---------------------

After starting MW4 the first time you will see the main window. It consists of 4 areas to be
used:

.. image:: _static/explain_main_1.png
    :align: center

Area 1
^^^^^^

...describes the actual status of the important devices for modeling, shows status text
outputs from devices and open / shows status / closes additional windows for further work.

Area 2
^^^^^^
...shows actual computer time, UTC, and the actual profile. In header section there is
hint if MW4 work actually in online (internet connected) or offline mode.

Area 3
^^^^^^
...manages loading / saving profiles, boot and shutdown of the mount (if WOL is enabled
and the MAC address of the mount is known)

Area 4
^^^^^^
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

Environ Tab
-----------
If you have environment sensors connected and configured you could see the overview in the
environment tab. The tab content is dynamically, the more connections you have, the more you
will see. The example is the maximum MW4 could support.

.. image:: _static/explain_environ_tab.png
    :align: center

Area 1
^^^^^^
Data of all different configured sources are shown here. If a source has no connection or
receives no data, the frame will turn red.

+----------+----------------+-----------------------------------------------------+
| source   | device         | remarks                                             |
+----------+----------------+-----------------------------------------------------+
| SkyMeter | Unihedron SQM  | for compensation it's gathering temperature as well |
+----------+----------------+-----------------------------------------------------+
| Power    | Pegasus UPB1/2 | both version are supported                          |
+----------+----------------+-----------------------------------------------------+
| Weather  | OpenWeatherMap | API needed, the pressure is at mount level !        |
+----------+----------------+-----------------------------------------------------+
| Sensor   | MBox, MGBox    | if connected as INDI external device, compatibles   |
+----------+----------------+-----------------------------------------------------+
| Direct   | MGBox          | if connected via GPS connector to mount             |
+----------+----------------+-----------------------------------------------------+

Area 2
^^^^^^
THis is the data the mount is working with. In the mount box there is the actual refraction
data the mount knows. You could set the refraction update method in this area or push the
data manually to the mount. Continuously means at any state, but filtered with a moving
average filter of 60s length. No tracking means updating whenever new data is coming, but
only when the mount is not in tracking state.

If no source for updating the refraction data is available, but needed, this part will turn
red. The update mode is set in mount computer if "Direct" source is selected or done through
MW4 for all others sources.

Area 3
^^^^^^
If you have a online connection enabled, you could see the weather forecast for your
location from clearoutside. Thanks to these guy to agree on this integration. The location
is automatically set to the location of your mount.

Area 4:
^^^^^^^
If a source frame has a checkbox, this source could be chosen for using it's data for
refraction update. As you might have different ones, you have the choice.

Model Build Tab
---------------

.. image:: _static/explain_model_build_tab.png
    :align: center

Manage Model Tab
----------------

.. image:: _static/explain_manage_model_tab.png
    :align: center

Satellite Tab
-------------

.. image:: _static/explain_satellite_tab.png
    :align: center

Power Tab
---------

.. image:: _static/explain_power_tab.png
    :align: center

Relay Tab
---------

Should be added later.

Tools Tab
---------

.. image:: _static/explain_tools_tab.png
    :align: center