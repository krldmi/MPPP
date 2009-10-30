==========================
 Writing your own plugins
==========================

It is possible to write plugins in order to add support for more satellites.

* A plugin consists of an implementation of a subclass of SatelliteSnapshot.
* It should contain a `load()` method to load channels into the object
* It can also redifine or add new RGB composite methods.

For an example, see :ref:`met09`
