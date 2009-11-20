#!/usr/bin/env python
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
                'report'],
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
