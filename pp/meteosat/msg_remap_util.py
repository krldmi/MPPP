
import numpy

# ----------------------------------------
class SeviriChannelData:
    def __init__(self):
        self.info = {}
        self.info["description"] = "Unkown SEVIRI channel data"
        self.info["nodata"] = -9999
        self.info["num_of_columns"] = 0
        self.info["num_of_rows"] = 0
        self.bt=None
        self.ref=None
        self.rad=None


# ------------------------------------------------------------------
def read_msg_lonlat(geofile):
    
    fd = open(geofile,"r")
    s = fd.read()
    fd.close()
    retv = numpy.fromstring(s,"f")
    retv = numpy.reshape(retv,(ROWS,COLS))
    del s
    return retv


# --------------------------------------------------------------------
def get_bit_from_flags(arr,nbit):
    a = numpy.bitwise_and(numpy.right_shift(arr,nbit),1)
    return a.astype('b')

