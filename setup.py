#!/usr/bin/env python

from setuptools import setup, Extension
import os.path

MSG_PATH = '/home/a001673/usr/src/msg/'
MSG_INCLUDE = os.path.join(MSG_PATH, 'include')
MSG_LIB = os.path.join(MSG_PATH, 'bin')
NUMPY_DIR

NAME = 'PostProcessing'

setup(name=NAME,
      version='0.2.0a1',
      description='Meteorological post processing package',
      author='Adam Dybbroe, Martin Raspaud',
      author_email='martin.raspaud@smhi.se',
      packages=['pp', 'pp.geo_image','pp.meteosat','pp.satellite'],
      package_data={'pp': ['doc/Makefile','doc/source/*.rst','doc/source/*.py']},
      scripts=['bin/meteosat_pp', 'bin/msg_pp'],
      data_files=[('etc',['etc/products.py']),
                  ('etc',['etc/msgpp_config.py']),
                  ('share/doc/'+NAME+'/',
                   ['pp/doc/Makefile',
                    'pp/doc/source/conf.py',
                    'pp/doc/source/coverage.rst',
                    'pp/doc/source/geo_image.rst',
                    'pp/doc/source/image.rst',
                    'pp/doc/source/index.rst',
                    'pp/doc/source/meteosat09.rst',
                    'pp/doc/source/misc_utils.rst',
                    'pp/doc/source/palettes.rst',
                    'pp/doc/source/quickstart.rst',
                    'pp/doc/source/rs_images.rst',
                    'pp/doc/source/sat_ext.rst',
                    'pp/doc/source/satellite.rst',
                    'pp/doc/source/satellites_h.rst',
                    'pp/doc/source/time_utils.rst'])],
      ext_modules=[Extension('pp.meteosat.py_msg',
                             ['pp/meteosat/py_msgmodule.c'],
                             include_dirs=[MSG_INCLUDE,'/usr/lib64/python2.5/site-packages/numpy/core/include'],
                             libraries=['nwclib','msg','m'],
                             library_dirs=[MSG_LIB])],
      #install_requires=['acpg (>=2.03)']
      
      )
