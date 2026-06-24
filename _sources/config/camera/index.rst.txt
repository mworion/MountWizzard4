Adding the camera
=================
For adding devices like the camera select the Sett. / Conf. tab in the main menu
and there select the devices tab. For the following explanation we would like to
connect a camera, a filter and adding a link to the mount as well. The mount link
is only used for reading the parameters of the mount driver of your setup (e.g.
focal length, aperture).

.. image:: image/camera_01.png
    :align: center
    :scale: 71%

In core devices select Setup für Camera. A popup shows up. Please fill in the ip
address of the INDI or ALPACA server, where your devices are connected to.

.. image:: image/camera_02.png
    :align: center
    :scale: 71%

If you are using INDI, you search for INDI camera devices by clicking on the
search button. Once you finished searching by pressing OK button, a list of
available devices will be populated. From the list choose the device and finish
the setup with OK button.

.. image:: image/camera_03.png
    :align: center
    :scale: 71%

The selected camera will be highlighted green in the drop down menu and in the
status as well. Once you configured the camera, the selection list will be stored
for later use. If you want to disable the camera, please select device disabled
in the menu.

.. image:: image/camera_04.png
    :align: center
    :scale: 71%

MountWizzard4 will now try to connect to the device and show green light
whenever a connection is established.

Do the steps 1 - 5 for all devices you need to configure. All configuration are
save when leaving MountWizzard4 with Save/Quit button or just when saving the
profile. You can add or change any config later on at any time.

Using N.I.N.A. as device
------------------------
In addition to the standard frameworks to interface to devices, MountWizzard4
could use Nighttime Imaging (N.I.N.A.) as a driver for devices attached to them.

.. note:: MountWizzard4 uses all necessary data from the FITS of the images
          taken by the external apps. Please make sure, that the FITS header
          contains this information, especially the focal length, the pixel
          size. Otherwise plate solving will fail. As both applications do not
          transfer their images to MountWizzard4, you have to ensure that the
          FITS files are stored on your local disk and MountWizzard4 has access.

Basically MountWizzard4 interface N.I.N.A. through it's alpaca plugin and let
them control the devices. This means, that you have to install the Alpaca plugin
for N.I.N.A. and enable it, but you could also use other devices than cameras,
e.g. filter wheel, focuser, dome, etc. as well.

Preparation for using NINA 3.x as ALPACA device
------------------------------------------
N.I.N.A. 3.x realizes this feature in a separate plugin. The plugin is called
Alpaca:

.. image:: image/sgpro-control.png
    :align: center
    :scale: 71%

Please install this plugin first and enable it.
