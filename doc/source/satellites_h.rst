============
 Satellites
============

The satellite interface is the core of the postprocessing package.

Generic satellite library
=========================

The :mod:`satellite` module
---------------------------

.. automodule:: pp.satellite.satellite
   :members:
   :undoc-members:

Projecting: the :mod:`coverage` module
--------------------------------------

.. automodule:: pp.satellite.coverage
   :members:
   :undoc-members:

Colors: the :mod:`palettes` module
----------------------------------

.. automodule:: pp.satellite.palettes
   :members:
   :undoc-members:

The Meteosat plugin
===================

Main implementation
-------------------

.. automodule:: pp.meteosat.meteosat09
   :members:
   :undoc-members:

Cloudtype channel
-----------------

.. automodule:: pp.meteosat.msg_ctype
   :members:
   :undoc-members:

Cloudtype for Nordrad
---------------------

.. automodule:: pp.meteosat.msg_ctype2radar
   :members:
   :undoc-members:

CTTH channel
------------

.. automodule:: pp.meteosat.msg_ctth
   :members:
   :undoc-members:

MSG interface
-------------

.. autofunction:: pp.meteosat.py_msg.get_channels(time_slot, region_name, channels, read_rad=None)
   
.. autofunction:: pp.meteosat.py_msg.lat_lon_from_region(region_name, channel)

.. autofunction:: pp.meteosat.py_msg.missing_value()


Time utilities
--------------

.. automodule:: pp.meteosat.time_utils
   :members:
   :undoc-members:


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
   :linenos:
