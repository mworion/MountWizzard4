Configuring MW4
===============
After installation of python3.7 and MW4 you could start the application. For the first
configuration of MW4 you should do the following steps:

Mount Connectivity
------------------

1. In the Sett./Conf. tab goto Mount / WeatherAPI and enter under Mount connectivity the IP
address of you mount.

2. Boot the mount manually and wait until the mount computer is ready.

3. MW4 will show for Mount connection a green light and enters the MAC Address for remote
boot via wake-on-lan (WOL).

4. Goto Misc / Audio tab and enable Internet online connection if you have access to internet

5. You should go to the main tab back and select the Mount tab and enable WakeOnLan in the
menu.

Adding devices
--------------
For adding devices select the Sett. / Conf. tab in the main menu and there select the
devices tab. For the following explanation we would like to connect a camera, a filter and
adding a link to the mount as well. The mount link is only used for reading the parameters
of the mount driver of your setup (e.g. focal length, aperture).

1. In core devices select Setup für Camera. A popup shows up.

2. Please fill in the ip address of the INDI or ALPACA server, where your devices are
connected to.

3. If you are using INDI, you search for INDI camera devices by clicking on the search
button. A list of available devices will be populated.

4. From the list choose the device and finish the setup with OK button.

5. Once you configured the camera, you could select the camera out of the camera list. If
you want to disable the camera, please select device disabled in the menu.

6. MW4 will try to connect to the device and show green light whenever a connection is
established.

7. Do the steps 1 - 5 for all devices you need to configure.


All configuration are save when leaving MW4 with Save/Quit button or just when saving the
profile. You can add or change any config later on at any time.