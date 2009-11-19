==========================
 Writing your own plugins
==========================

It is possible to write plugins in order to add support for more satellites.

* A plugin consists of an implementation of a subclass of SatelliteSnapshot.
* It should contain a `load()` method to load channels into the object and a
  `get_lat_lon()` method to retreive the 2D latitude and longitude grids in
  degrees (for re-projections).
* It can also redifine or add new RGB composite methods.

For an example, here is the simplistic Noaa handling plugin, using AHAMAP to
read files:

.. literalinclude:: ../../pp/noaa/noaa.py
