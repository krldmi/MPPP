#!/usr/bin/env python

from distutils.core import setup, Extension
from conf import MSG_INCLUDE, MSG_LIB

setup(name='PostProcessing',
      version='0.2.0a1',
      description='Meteorological post processing package',
      author='Adam Dybbroe, Martin Raspaud',
      author_email='martin.raspaud@smhi.se',
      packages=['pp', 'pp.geo_image','pp.meteosat','pp.satellite'],
      package_data={'pp': ['doc/Makefile','doc/source/*.rst','doc/source/*.py']},
      data_files=[('etc',['etc/products.py'])],
      ext_modules=[Extension('pp.meteosat.py_msg',
                             ['pp/meteosat/py_msgmodule.c'],
                             include_dirs=[MSG_INCLUDE,'/usr/lib64/python2.5/site-packages/numpy/core/include'],
                             libraries=['nwclib','msg','m'],
                             library_dirs=[MSG_LIB])],
      requires=['acpg (>=2.03)']
      
      )
