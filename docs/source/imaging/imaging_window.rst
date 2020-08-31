Image Window
============
The imaging window shows FITS files loaded from disk or images exposed manually or during
model build. It is split in different areas to work with.

.. image:: image/image.png
    :align: center
    :scale: 71%

Area 1: Image exposing and solving
----------------------------------
MW4 supports single (expose 1) and multiple (expose N) exposures. Continuous imaging could be
stopped with abort. You also could explicitly load a fits file (extension .fit or .fits).
If you have a plate solver (e.g. ASTAP) installed, you could solve the actual displayed
image. The solved results are shown in message window. If you would like to add the results to
the image, please check "embed data". This will make MW4 to write the plate solving results
in the fits header of the file.

.. warning::
    Please be aware that MW4 will write the data to be embedded directly in the FITS file
    without making a copy of the file!

When "auto solve" is checked, MW4 will automatically plate solve every new picture and show
or embed the results in the message window or fits header.

A simple stacking method is available when mount is in tracking and keeps point accurate.
When "stacking" is checked, MW4 will add all exposed images (expose N running) and calculate
the mean of the image.

Area 2: FITS Header entries
---------------------------
Some of the FITS header entry of the actual image are shown.

Area 3: Image attributes
------------------------
MW4 calculates and extracts some image attributes. For example if a WCS header information
is available, the distortion parameters are present or the actual image is flipped with
regard to real position in sky.

Area 4: Image display
---------------------
Show the image and it's different view selected in area 5. For standard view the scale is
pixel with 0/0 to be the center of the image. There will be a colorbar in each view with the
values of the image.

Area 5: View options
--------------------
For the image you have different options to alter the main view of the image:

.. list-table:: Image views
    :widths: 30, 70
    :header-rows: 1

    *   - Drop down entry
        - Explanation
    *   - Image
        - standard visualization of the image in greyscale. MW4 does not support colors
    *   - Image & WCS coordinates
        - if distortion parameters are included, MW4 will show the RA / DEC coordinates
    *   - Image & detected sources
        - an overlay of the image with the extracted sources (stars) as circles
    *   - Photometry - Sharpness
        - sextractor based algorithm: value for referencing the sharpness (s.below)
    *   - Photometry - Roundness
        - sextractor based algorithm: value for roundness of the sources
    *   - Photometry - Flux
        - sextractor based algorithm: value for flux of the sources

Some examples for the windows
-----------------------------

View Image with WCS distortion:

.. image:: image/image_distortion2.png
    :align: center
    :scale: 71%

View Image with sources:

.. image:: image/show_sources.png
    :align: center
    :scale: 71%

View image with photometry sharpness

.. image:: image/show_sharpness.png
    :align: center
    :scale: 71%

View image with photometry roundness

.. image:: image/show_roundness.png
    :align: center
    :scale: 71%

View image with photometry flux

.. image:: image/show_flux.png
    :align: center
    :scale: 71%

View image with different zoom

.. image:: image/zoom_2.png
    :align: center
    :scale: 71%

View image with different color scheme

.. image:: image/color_1.png
    :align: center
    :scale: 71%




