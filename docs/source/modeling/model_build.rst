Running a model build
=====================
After you have selected you model points, MW4 could automatically run through the
points and generate the data to build a model. These are steps you could basically
all manual as the final model calculation itself is done in the mount computer!
There are two different ways offered from 10micron to build a model:

.. hlist::
    :columns: 1

    * Incremental
    * Batch

In incremental model build, each new point will start a recalculation of the model
in the mount. This behavior is also called sync refine, as with each point the
model is processed.

In batch model build, a complete set of point and their data are transferred to
the mount computer, which calculates from this data a new model.

In result both variant will produce the same model with the same quality. The
difference is the way and the context you are working in. MW4 uses the batch model
build as there are advantages (not in the model quality) in the automatic handling
of point data.

.. image:: image/model_build.png
    :align: center
    :scale: 71%

In the model build tab on the left, that actual model spec from the mount computer
is shown. If you are in an early stage of your setup, you might use some of the
hints given to refine and tune your mechanical setup before building your final
model for imaging.

.. note::   All values which are show in these graphs were calculated by the mount
            computer itself and just read out and displayed by MW4. As the 10micron
            algorithm of the model optimizer is not know. The given hints are
            observations.

.. warning::    Any changes in your mechanical setup invalidates the model!

Using model datafiles
---------------------
MW4 stores for each model build run all data (and some more for analyse) to build
a mount model. With this data you could rebuild at any time you mount model from
scratch if you for example deleted to much points during optimisation or other
reasons.

In addition you have the chance to combine multiple model runs to a single mount
model! Please think of the maximum of 100 point the mount computer will handle to
calculate a mount model.

The warning about the invalidation of the model when mechanical changes are made
are true for this step as well. Combining model data from different mechanical
setups lead into an invalid model. Rebuilding a model from old data when
mechanical changes were made result also in an incorrect model.

Fast Align
----------
There is a way to adjust an existing model to a certain sphere position. If you
choose fast align, MW4 will do for the actual position an image, plate solve it an
align the model to the solved coordinates. This means the whole model is move in a
way, that the actual pointing coordinates and solved coordinates are equal. But
this changes model pointing for all other position in the sky as well without
knowing if this shift really fits there.

.. note::   Fast align is a step to adjust quickly a reasonable model to an actual
            pointing position. This action is not a model build process! You most
            probably loose the pointing accuracy of you model!

