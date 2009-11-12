"""Miscellaneous image processing tools.
"""
import numpy
import logging

LOG = logging.getLogger('pp.geo_image')

def gamma_correction(arr, gamma):
    """Perform gamma correction *g* to an array *arr*, which is assumed
    to be in the range [0.0,1.0], and return the resulting array (same
    range). 
    """
    return arr ** (1.0 / gamma)

def crude_stretch(arr, norm = 1, amin = None, amax = None):
    """Perform simple linear stretching (without any cutoff) and normalize."""

    if(amin is None):
        amin = arr.min()
    if(amax is None):
        amax = arr.max()

    res = (arr - amin) * (norm * 1.0) / (amax - amin)
    res = numpy.where(res > norm, norm, res)
    res = numpy.where(res < 0, 0, res)

    return res
