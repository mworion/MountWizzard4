Model building remarks
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

Step 1/3
^^^^^^^^
With a small model with low number of points you could do the setup, which is basically polar
alignment. You could extend this for leveling or ortho align etc.) You are not limited to 3
stars. Beside a average distribution over the sky you could alter stars location according
to visibility or other constraints. Once you reach the performance you think it's OK, you
could go for step 2. Please consider the amount of time used against the improvements for
each additional iteration step. If you have a setup which is stable and / or has repeatable
align conditions like a fixed pier you could omit the first step and directly start over to
step 2.

Step 2/3
^^^^^^^^
There were multiple choices to define the alignment stars for your model. All selections
take care of visual constraints (horizon mask) or other limitation. MW4 tries to
optimize the slewing path, order and functions in order to minimize the time for modeling.
In general it should be possible to to 45 point within 15 minutes. So doing 2-3 points more
should not cause any big time delay.

Step 3/3
^^^^^^^^
Another difference you might discover: I do not build the model step by step over all the
stars, I just make all the slewing work, images and solve in parallel and than process them
to the mount. As you have all the data for a model collected, you could redo any model
making session just with the data already saved on your computer.


Summary of comments to model build:

Per:
Don't overdo this now. First of all, model point deletion should only be carried out if very
few points have large errors. If the map looks lke it does above after deletion then
something  is wrong in the rig, as the mount clearly gets high errors in specific regions.
The model point selection above is also kind of funny. Why so many near zenith? That is the
place that is most difficult to measure. Mathematically, it still does not matter which
order you run the points in. It all comes out the same way whever order you do it in. There
is, however, one important factor that may produce different results depending on the order,
and that is random flexure. Running your models smoothly in ever increasing alt without
large  scope movements will give better results. Jumping back and forth an flipping all the
time will give worse results - or better if the random flex is neutralized by the violent
moves. You see? There is no easy answer, no simple "42". If you get better or worse results
depending on the order of the points, then you should go with the one that produces the
best results. OK, back to point deletion. Don't over-do that! Check if here is a single or
just a very few points that stick out. They can be deleted. If there are many or you lose a
lot of them in an iterative removal, then you need to check everything and rerun the model.


Needless to say, the jump from almost 450" in Dec to 3.65" is a drastic one. After the run
is complete, the first three points report single digit errors (low single digits), which
is expected behavior. What the extra align procedure for the first three points does is
performed anyway by the mount at a later stage in the model process, and is compensated for
(nullified) as the actual base points are added to the, as of yet, non-existent model, in
effect adding nothing.

I know that TPoint reports the exact model terms that it finds and agree that it would be
useful information. In order for that procedure to be meaningful, the encoder offsets need
to be discovered and effectively compensated for, and accomplishing that would involve
having a basic model in place in the mount and running it in single axis tracking with
refraction off. I actually think that the basic model in the mount would disturb the  TPoint
calculations, but I am also quite confident that the information obtained from the process
would be quite useful in finding flex issues. Sadly, I do not have the time for that
experiment right now as I am choked with other projects as well as "real" work.

The difference between TPoint and the 10Micron implementation is, as per my current
understanding, that the latter sports a much more advanced rotational matrix   which yields
higher precision. The downside is that there is no reporting of the term results,  something
that would put it on par with TPoint in terms of reporting. I will correspond with the
"firmware department" and ventilate my views on that ;)



I can confirm this. There are 11 terms, and all the normal geometric ones are the same as
TPoint (IH, ID, CH, NP, ME and MA) but they are implemented with a more full-featured and
more accurate rotational model. The rotational matrix used allows for higher precision even
with large polar misalignment.
The number of model terms used is NOT an indication of model quality, but the expected RMS
surely is.

When I run my GM2000HPS II with the TEC-140, I usually get an RMS of around 5-6" without
point deletion. The TEC and its imaging train is usable as crowbar as well - very, very
sturdy! I often get 22 model terms, most likely with very small factors because of the rig
stability, but there still has to be measurable errors that need to be addressed. Again, a
perfect rig with perfect polar alignment would likely get a very small number of terms.

One factor that may very well affect the net result of a model run is the order of the
points.  From a purely mathematical standpoint, the order makes absolutely no difference,
but the rig may well behave differently if there is a pier flip between each point
triggering  some flex movements that would not happen if the points were done, say, in Az
order along the same altitude as much as possible.

I'll test the clock sync thing...
