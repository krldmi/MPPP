
import numpy

def get_bit_from_flags(arr,nbit):
    a = numpy.bitwise_and(numpy.right_shift(arr,nbit),1)
    return a.astype('b')

