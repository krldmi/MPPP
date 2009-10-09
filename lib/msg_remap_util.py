
from msgpp_config import *

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
# Read raw (unprojected BT&RAD or REF) SEVIRI channel data from hdf5
def read_raw_channels_hdf5(filename):
    import _pyhl
    aNodeList=_pyhl.read_nodelist(filename)
    aNodeList.selectAll()
    aNodeList.fetch()

    retv = SeviriChannelData()

    # Get the info dictionary:
    aNode=aNodeList.getNode("/info/description")
    retv.info["description"]=aNode.data()
    aNode=aNodeList.getNode("/info/nodata")
    retv.info["nodata"]=aNode.data()
    aNode=aNodeList.getNode("/info/num_of_columns")
    retv.info["num_of_columns"]=aNode.data()
    aNode=aNodeList.getNode("/info/num_of_rows")
    retv.info["num_of_rows"]=aNode.data()

    # Crude test to check if there are Tb's and Rad's or Refl's:
    if retv.info["description"].find("Reflectivities") >= 0:
        print "Channel is VIS/NIR"
        retv.ref = aNode=aNodeList.getNode("/ref").data()
    else:
        print "Channel is IR"
        retv.rad = aNode=aNodeList.getNode("/rad").data()
        retv.bt = aNode=aNodeList.getNode("/bt").data()
        
    return retv

# ------------------------------------------------------------------
def read_msg_lonlat(geofile):
    import numpy
    
    fd = open(geofile,"r")
    s = fd.read()
    fd.close()
    retv = numpy.fromstring(s,"f")
    retv = numpy.reshape(retv,(ROWS,COLS))
    del s
    return retv


# --------------------------------------------------------------------
def get_bit_from_flags(arr,nbit):
    import Numeric
    a = Numeric.bitwise_and(Numeric.right_shift(arr,nbit),1)
    return a.astype('b')

