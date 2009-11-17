#!/usr/bin/env python

from distutils.core import setup, Extension
import os.path

MSG_PATH = '/home/a001673/usr/src/msg/'
MSG_INCLUDE = os.path.join(MSG_PATH, 'include')
MSG_LIB = os.path.join(MSG_PATH, 'bin')

NAME = 'NWCSAF_MPPP'

setup(name=NAME,
      version='0.2.0a1',
      description='Meteorological post processing package',
      author='Adam Dybbroe, Martin Raspaud',
      author_email='martin.raspaud@smhi.se',
      packages=['pp', 'pp.geo_image','pp.meteosat','pp.satellite','pp.noaa','report'],
      package_data={'pp.meteosat': ['pp/meteosat/meteosat.cfg']},
      scripts=['bin/meteosat_pp', 'bin/msg_pp'],
      data_files=[('etc',['etc/products.py']),
                  ('etc',['etc/logging.cfg']),
                  ('etc',['etc/geo_image.cfg']),
                  ('etc',['etc/world_map.ascii']),
                  ('etc',['etc/offline.profile']),
                  ('etc',['etc/meteosat.cfg']),
                  ('etc',['etc/noaa.cfg']),
                  ('log',['log/README']),
                  ('share/doc/'+NAME+'/',
                   ['doc/Makefile',
                    'doc/source/conf.py',
                    'doc/source/coverage.rst',
                    'doc/source/geo_image.rst',
                    'doc/source/image.rst',
                    'doc/source/index.rst',
                    'doc/source/meteosat09.rst',
                    'doc/source/misc_utils.rst',
                    'doc/source/palettes.rst',
                    'doc/source/quickstart.rst',
                    'doc/source/rs_images.rst',
                    'doc/source/sat_ext.rst',
                    'doc/source/satellite.rst',
                    'doc/source/satellites_h.rst',
                    'doc/source/time_utils.rst'])],
      ext_modules=[Extension('pp.meteosat.py_msg',
                             ['pp/meteosat/py_msgmodule.c'],
                             include_dirs=[MSG_INCLUDE,'/usr/lib64/python2.5/site-packages/numpy/core/include'],
                             libraries=['nwclib','msg','m'],
                             library_dirs=[MSG_LIB])],
      requires=['acpg (>=2.03)','numpy (>=1.2.0)']
      )
