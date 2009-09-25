import os

import _pyhl
import _satproj
import area

from msgpp_config import *
from msg_communications import msgwrite_log

MODULE_ID = "MSG_COVERAGE"



# !!! This class is already defined in satproj, creating conflics if modified !

class SatProjCov:
    def __init__(self):
        self.coverage=None
        self.colidx=None
        self.rowidx=None
        #self.in_area_id=None
        #self.out_area_id=None

def get_coverage(input_area_id, output_area_id, lon, lat,hr = False):
    areaObj=area.area(output_area_id)
    
    if(hr):
        covfilename = "%s/cst/msg_coverage_%s_hr.%s.hdf"\
                      %(APPLDIR,input_area_id,output_area_id)
    else:
        covfilename = "%s/cst/msg_coverage_%s.%s.hdf"\
                      %(APPLDIR,input_area_id,output_area_id)
    
    if not os.path.exists(covfilename):
        msgwrite_log("INFO","Generate MSG coverage and store in file...",moduleid=MODULE_ID)
        coverage_data = _satproj.create_coverage(areaObj,lon,lat,1)
        #coverage_data.in_area_id = input_area_id
        #coverage_data.out_area_id = output_area_id
        write_coverage(coverage_data,covfilename,input_area_id,output_area_id)
    else:
        msgwrite_log("INFO","Read the MSG coverage from file...",moduleid=MODULE_ID)
        coverage_data,info = read_coverage(covfilename)
        #coverage_data.in_area_id = input_area_id
        #coverage_data.out_area_id = output_area_id
        
    return coverage_data

def write_coverage(covIn,filename,in_area_id, out_area_id):
        
    a=_pyhl.nodelist()

    b=_pyhl.node(_pyhl.GROUP_ID,"/info")
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/description")
    b.setScalarValue(-1,
                      "MSG coverage from area %s on to area %s"
                      %(in_area_id,out_area_id),
                      "string",-1)
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

def read_coverage(filename):

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
    retv.coverage = coverage.astype('b')
    retv.rowidx = rowidx.astype('h')
    retv.colidx = colidx.astype('h')

    return retv,info
