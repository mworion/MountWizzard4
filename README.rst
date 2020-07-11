MountWizzard4
=============

Overview
--------
Welcome to MountWizzard4 is a utility for 10micron users for improving the workflow for
astronomy work and imaging runs on Windows, OSx and Linux (Ubuntu tested). As a python
application, it should run in all environments supporting python 3.6-3.8 and PyQt5 as a Gui
framework.

For being fully operational, MW4 needs:

INDI server(s) (see: https://indilib.org) where your devices are connected to.

ASCOM Alpaca remote server (see: https://ascom-standards.org/Developer/Alpaca.htm)
abstracting your ASCOM devices or devices which speak native ASCOM Alpaca if you want to
connect over IP with your environment.

For the core devices there is fom 0.150.16 on native ASCOM support (Windows platform only).
Please be reminded, that ASCOM has 32bit and 64bit driver implementations and MW4 could also
be installed in 32bit or 64 bit python environment. They could be not be mixed! 32bit python
supports only 32bit drivers and vice versa. Normally this should not be an issue...

In addition an online connection is used for some services which might be very helpful.

It is recommended to use mount firmware 2.16 (ideally 2.16.11) or later as some of the
functions don't work with older firmware versions. It should not be a problem using older
versions. A HW pre2012 might also have some issues.

Documentation
-------------
|DOCS|

The online documentation for MW4: https://mountwizzard4.readthedocs.io.

Installing: https://mountwizzard4.readthedocs.io/en/latest/install/index.html

Changelog: https://mountwizzard4.readthedocs.io/en/latest/changelog.html

There is also a PDF version available for download
here: https://mountwizzard4.readthedocs.io/_/downloads/en/latest/pdf/.

There are some videos (more to come) on youtube in the channel:
https://www.youtube.com/channel/UCJD-5qdLEcBTCugltqw1hXA/, but they are also linked in the
online documentation.


Version, build and code coverage status
---------------------------------------
|PYPI_VERSION| |DownLoadsAbs| |DownLoadsMonth|

|PYTEST MacOS| |PYTEST Win| |CODECOV|

|CODE_QUALITY_PYTHON| |CODE_QUALITY_ALERTS|

Coverage chart: 

|CODECOV_CHART|

|6U| |6W| |6M|

|7U| |7W| |7M|

|8U| |8W| |8M|

Bug reports
-----------
Please report bugs only under issues: https://github.com/mworion/MountWizzard4/issues.
Any feedback welcome!

Finally
-------
MountWizzard4 is still in beta development. The use this software is at your own risk! No
responsibility for damages to your mount or other equipment or your environment, please take
care yourself!

Hope this tool makes fun and helps for your hobby,

CS Michel

.. |DOCS| image:: https://readthedocs.org/projects/mountwizzard4/badge/?version=latest
    :target: https://mountwizzard4.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |PYTEST MacOS| image:: https://github.com/mworion/MountWizzard4/workflows/UnitTest%20MacOS/badge.svg
.. |PYTEST WIN| image:: https://github.com/mworion/MountWizzard4/workflows/UnitTest%20Win/badge.svg
.. |CODECOV| image:: https://codecov.io/gh/mworion/MountWizzard4/branch/master/graph/badge.svg
.. |CODECOV_CHART| image:: https://codecov.io/gh/mworion/MountWizzard4/branch/master/graphs/icicle.svg
    :target: https://codecov.io/gh/mworion/MountWizzard4
    :width: 80%
    :align: top

.. |CODE_QUALITY_ALERTS| image:: https://img.shields.io/lgtm/alerts/g/mworion/MountWizzard4.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/mworion/MountWizzard4/latest/files/?sort=name&dir=ASC&mode=heatmap&showExcluded=false
.. |CODE_QUALITY_PYTHON| image:: https://img.shields.io/lgtm/grade/python/g/mworion/MountWizzard4.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/mworion/MountWizzard4/?mode=list

.. |6U| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.6%20Ubuntu%20Package/badge.svg
.. |6W| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.6%20Windows%20Package/badge.svg
.. |6M| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.6%20MacOS%20Package/badge.svg
.. |7U| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.7%20Ubuntu%20Package/badge.svg
.. |7W| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.7%20Windows%20Package/badge.svg
.. |7M| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.7%20MacOS%20Package/badge.svg
.. |8U| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.8%20Ubuntu%20Package/badge.svg
.. |8W| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.8%20Windows%20Package/badge.svg
.. |8M| image:: https://github.com/mworion/MountWizzard4/workflows/Py3.8%20MacOS%20Package/badge.svg

.. |PYPI_VERSION| image:: https://img.shields.io/pypi/v/mountwizzard4.svg
    :target: https://pypi.python.org/pypi/mountwizzard4
    :alt: MountWizzard4's PyPI Status
    
.. |DownLoadsAbs| image:: https://pepy.tech/badge/mountwizzard4
    :target: https://pepy.tech/project/mountwizzard4
.. |DownLoadsMonth| image:: https://pepy.tech/badge/mountwizzard4/month
    :target: https://pepy.tech/project/mountwizzard4/month
