"""MSG utilities.
"""
import numpy

def get_bit_from_flags(arr, nbit):
    """I don't know what this function does.
    """
    res = numpy.bitwise_and(numpy.right_shift(arr, nbit), 1)
    return res.astype('b')

