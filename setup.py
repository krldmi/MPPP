#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009.

# SMHI,
# Folkborgsvägen 1,
# Norrköping, 
# Sweden

# Author(s):
 
#   Martin Raspaud <martin.raspaud@smhi.se>
#   Adam Dybbroe <adam.dybbroe@smhi.se>

# This file is part of the MPPP.

# MPPP is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MPPP is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MPPP.  If not, see <http://www.gnu.org/licenses/>.

"""Setup file for MPPP.
"""

from distutils.core import setup, Extension
import os.path
import ConfigParser

BASE_PATH = os.path.sep.join(os.path.dirname(
    os.path.realpath(__file__)).split(os.path.sep))

CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(BASE_PATH, "etc", "meteosat.cfg"))

MSG_LIB = CONF.get('dirs_in', 'msg_lib')
MSG_INC = CONF.get('dirs_in', 'msg_inc')

CONF.read(os.path.join(BASE_PATH, "setup.cfg"))
NUMPY_INC = CONF.get('numpy', 'numpy_inc')
NAME = 'NWCSAF_MPPP'

setup(name=NAME,
      version='0.2.0a1',
      description='Meteorological post processing package',
      author='Adam Dybbroe, Martin Raspaud',
      author_email='martin.raspaud@smhi.se',
      packages=['pp', 'pp.geo_image', 'pp.meteosat', 'pp.satellite', 'pp.noaa',
                'pp.metop', 'report'],
      package_data={'pp.meteosat': ['pp/meteosat/meteosat.cfg']},
      scripts=['bin/meteosat_pp'],
      data_files=[('etc',['etc/products.py']),
                  ('etc',['etc/logging.cfg']),
                  ('etc',['etc/geo_image.cfg']),
                  ('etc',['etc/world_map.ascii']),
                  ('etc',['etc/offline.profile']),
                  ('etc',['etc/meteosat.cfg']),
                  ('etc',['etc/metop.cfg']),
                  ('etc',['etc/noaa.cfg']),
                  ('log',['log/README']),
                  ('share/doc/'+NAME+'/',
                   ['doc/Makefile',
                    'doc/source/conf.py',
                    'doc/source/index.rst',
                    'doc/source/install.rst',
                    'doc/source/quickstart.rst',
                    'doc/source/satellites_h.rst',
                    'doc/source/geo_image.rst',
                    'doc/source/image.rst',
                    'doc/source/rs_images.rst'])],
      ext_modules=[Extension('pp.meteosat.py_msg',
                             ['pp/meteosat/py_msgmodule.c'],
                             include_dirs=[MSG_INC,
                                           NUMPY_INC],
                             libraries=['nwclib','msg','m'],
                             library_dirs=[MSG_LIB])],
      requires=['acpg (>=2.03)','numpy (>=1.2.0)']
      )
