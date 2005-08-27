
from msgpp_config import *

# ----------------------------------------
class SatProjCov:
    def __init__(self):
        self.coverage=None
        self.colidx=None
        self.rowidx=None
    

# ------------------------------------------------------------------
def writeCoverage(covIn,filename,inAid,outAid):
    import _pyhl
        
    a=_pyhl.nodelist()

    b=_pyhl.node(_pyhl.GROUP_ID,"/info")
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/description")
    b.setScalarValue(-1,"MSG coverage from area %s on to area %s"%(inAid,outAid),"string",-1)
    a.addNode(b)
    
    shape=[covIn.coverage.shape[0],covIn.coverage.shape[1]]
    b=_pyhl.node(_pyhl.DATASET_ID,"/coverage")
    b.setArrayValue(1,shape,covIn.coverage,"uchar",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.DATASET_ID,"/rowidx")
    b.setArrayValue(1,shape,covIn.rowidx,"ushort",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.DATASET_ID,"/colidx")
    b.setArrayValue(1,shape,covIn.colidx,"ushort",-1)
    a.addNode(b)

    a.write(filename,COMPRESS_LVL)
    
    return

# ------------------------------------------------------------------
def readCoverage(filename):
    import _pyhl

    a=_pyhl.read_nodelist(filename)
    b=a.getNodeNames()
    
    a.selectNode("/info/description")
    a.selectNode("/coverage")
    a.selectNode("/rowidx")
    a.selectNode("/colidx")
    a.fetch()

    info={}
    c=a.getNode("/info/description");
    d=c.data()
    info["description"]=d

    c=a.getNode("/coverage")
    coverage=c.data()
    c=a.getNode("/rowidx")
    rowidx=c.data()
    c=a.getNode("/colidx")
    colidx=c.data()
    
    retv = SatProjCov()
    retv.coverage = coverage.astype('1')
    retv.rowidx = rowidx.astype('s')
    retv.colidx = colidx.astype('s')

    return retv,info

# ------------------------------------------------------------------
def read_msg_lonlat(geofile):
    import Numeric
    
    fd = open(geofile,"r")
    s = fd.read()
    fd.close()
    retv = Numeric.fromstring(s,"f")
    retv = Numeric.reshape(retv,(ROWS,COLS))
    del s
    return retv

# --------------------------------------------------------------------
def get_bit_from_flags(arr,nbit):
    import Numeric
    a = Numeric.bitwise_and(Numeric.right_shift(arr,nbit),1)
    return a.astype('b')

