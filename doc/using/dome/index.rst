Dome
====

MountWizzard4 starts slewing the dome in parallel to the mount as it knows where
the mount will land. Normally it should be able to detect how long the dome
slews. The waiting time for the dome should be only relevant if dome movements
influence mount by vibrations. It could be the case that the slewing signal has
some specialities.

Sorting there are some optimizations to be set in MountWizzard4. Default ist
without dome and it sorts for minimum mount slews distance. If you are using a
dome, dome slews might be more worth to be optimized (reduced) than the mount
moves, so you could sort the model points in ascending azimuth of the dome.
This means sorting not the raw positions, but the ones the dome need to be when
the mount finished slewing. This ordering should take care for meridian
positions, geometrical corrections and so on. In principle this sort simulates
a full model run, calculates the mount position, calcs the resulting dome
positions and sorts the model points that you get ascending azimuth for the dome.