Dome
====

MountWizzard4 starts slewing the dome in parallel to the mount as it knows where
the mount will land. Normally it should be able to detect how long the dome
slews. The waiting time for the dome should be only relevant if dome movements
influence mount by vibrations. It could be the case that the slewing signal has
some specialities.

Sorting there are some optimizations to be set in MountWizzard4. Default ist
without dome and it sorts for minimum mount slews distance.

.. image:: image/dome1.png
    :align: center
    :scale: 71%