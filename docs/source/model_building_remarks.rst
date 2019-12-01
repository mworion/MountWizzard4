Model Building Remarks
======================
First of all a disclaimer to all what I have written here:

I only focus on model building with tool support, so no words about manual model building.
I don't know the internal algorithms of the 10micron mount how the calculate their
corrections. So many of the hints derive from pure logical or mathematical approaches and
even there I personally might have some misconceptions or make some errors. My setup - as I
mention it as reference - is described in: my setup

So my goal in model building is quite simple: I'm lazy in doing setups, so I want a
solutions which gives me a correction model most accurate in minimum of time automatically.
I rely heavily on the corrections capability on the 10micron mounts, so I use them always
with dual tracking on. For doing a setup there are many things to think of beside the model
(leveling, rigidity etc.). Keep them perfect, but I don't talk about them. So this results
in two tasks I have to do to get a model to do unguided images: Polar alignment and the
model for correction itself.

Remarks about model building from the origin: model maker
---------------------------------------------------------
As there was (and is) ModelMaker from Per in the past (which influenced me to buy the mount)
some more solutions like ModelCreator from Martin evolved. I'm doing MountWizzard work the
way like I use it personally, but if there are ideas which should be realized, please let
me know.

This said, I follow a different path in modeling for 10micron mount than in the past. There
was always the first step by using 3 base points for the start. There is no reason about
that but the fact that you need at least 3 stars to build a first model to get some
information about you polar alignment etc.

I refer to the Blog Filippo Riccio from 10micron:

https://www.10micron.eu/forum/viewtopic.php?f=16&t=846

He described how modeling in the mount works . Please read it carefully ! It might be to
complex to understand so I will abstract it a little bit (please forgive me if it is too
simple) and add some personal experiences:

Polar Alignment
---------------
For getting a polar alignment you need in minimum 3 alignment stars. If you have a bad
mechanical setup (leveling, etc), this might not be enough (even though you get calculated
numbers) If you choose the location of stars badly (to close, etc), the result will be bad,
too. Yes, you could use more points for first model for polar alignment. Sometimes this is
necessary. In my fixed pier setup when putting the mount on top of the pier, I only have to
use 3 stars to get a reasonable result.

.. note::   Please think of the main task: you would like to do a polar alignment! Please
            think of the mechanics of the orientations in the sky and remember
            what you would like to do. Does the choice of stars helps or not? Please don't
            think just adding more stars for a first model to do polar alignment will result
            automatically in the better result.

All the hints you get from the mount (how to turn knobs, alignment star) improve the
alignment. As the model is only an approximation for the error correction, it
will be not an one step approach. If you aim for the best result, please think of 2-3
iterations of the whole procedure. In my setup I normally need 2 Iterations for doing an
alignment which is good for 20-30 min exposures and have round stars.

Model build
-----------
The model correct for error. Some could be removed exactly, some not. The way is a
mathematically optimization method. In max the mount could calculate 22 terms (which means
two models of a set of 11 terms, one for WEST and one for EAST side). The algorithm of the
mount chooses the numbers -> you have no influence to it ! Sorry that's not true: from
mathematics: if you need 22 parameters for the model (for whatever reason the mount thinks),
you have to have at minimum 22 alignment stars or more. Otherwise this will not result in 22
parameters. Again like in polar alignment: think of what is the goal of this task. For sure
you would like to remove as much of the alignment error to be able to get unguided images.
This said: Choose stars in the region where the mount points during the overall imaging
sessions. Stars elsewhere obviously might not help in improving your actual imaging session.
Again this is not the whole truth. Because of mathematics optimization might lead to
unstable results if you have to narrow measurements. So some points who make a good average
helps the mathematics. For that reason I normally do about 40 points to cover that all.

Model optimization
------------------
Yes you could remove bad points from the model. But does it help ? Again from mathematics:
you bend an error curve like a metal plate over a rough surface to equalize it. If the is a
single stone under this plate -> approximation might be bad. So removing this stone might
help in getting a better approximation for the rest of the surface. But it is not good to
remove the gravel under the plate to improve just numbers in RMS! If I see large outliers in
alignment errors within an area which shows good numbers around, I remove that single point.
But not to much. In average I remove 2-5 points from a 60 point model max. Yes if you remove
a point the over RMS could rise ! That's because the whole model is newly calculated and
that's no subtraction of a bad point.

.. note::   To sum it up: you have the think about your targets and don't just shoot the
            numbers!

Impact to development to MountWizzard4
--------------------------------------
In MW3 I split the workflow into two parts: The Initial Model (for setup, polar alignment
etc.) and the Full Model (building the model for imaging). This I changed in MW4. I asked
myself why should I split. All points are at the end from the same type in mount. All points
are in the same optimization algorithm in the mount. The only difference is the number of
point you would like to use.

As MW4 like the versions before use a direct communication to the mount all topics about sync
behaviour you don't have to take care yourself. Honestly speaking MW4 uses a different way
for model build which does not need these settings.

Step 1
^^^^^^
With a small model with low number of points you could do the setup, which is basically polar
alignment. You could extend this for leveling or ortho align etc.) You are not limited to 3
stars. Beside a average distribution over the sky you could alter stars location according
to visibility or other constraints. Once you reach the performance you think it's OK, you
could go for step 2. Please consider the amount of time used against the improvements for
each additional iteration step. If you have a setup which is stable and / or has repeatable
align conditions like a fixed pier you could omit the first step and directly start over to
step 2.

Step 2
^^^^^^
There were multiple choices to define the alignment stars for your model. All selections
take care of visual constraints (horizon mask) or other limitation. MW4 tries to
optimize the slewing path, order and functions in order to minimize the time for modeling.
In general it should be possible to to 45 point within 15 minutes. So doing 2-3 points more
should not cause any big time delay.

Step 3
^^^^^^
Another difference you might discover: I do not build the model step by step over all the
stars, I just make all the slewing work, images and solve in parallel and than process them
to the mount. As you have all the data for a model collected, you could redo any model
making session just with the data already saved on your computer.